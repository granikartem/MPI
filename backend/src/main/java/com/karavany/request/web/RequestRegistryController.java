package com.karavany.request.web;

import com.karavany.request.domain.ActorRole;
import com.karavany.request.domain.AttentionFlag;
import com.karavany.request.domain.RegistryEntry;
import com.karavany.request.domain.RequestRegistry;
import com.karavany.request.domain.RequestStatusMachine;
import com.karavany.request.service.RequestRegistryService;
import com.karavany.request.service.RequestRegistryService.RegistryView;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.method.annotation.MethodArgumentTypeMismatchException;

import java.time.LocalDate;
import java.time.OffsetDateTime;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;

@RestController
@RequestMapping("/api/requests/registry")
public class RequestRegistryController {

    private final RequestRegistryService service;

    public RequestRegistryController(RequestRegistryService service) {
        this.service = service;
    }

    @GetMapping
    public RegistryResponse registry(@RequestParam(required = false) UUID organizationId,
                                     @RequestParam(required = false) String scope,
                                     @RequestParam(required = false) List<String> status,
                                     @RequestParam(required = false) List<String> riskLevel,
                                     @RequestParam(required = false, defaultValue = "false") Boolean attentionOnly,
                                     @RequestParam(required = false) String sort,
                                     @RequestParam(required = false) Integer limit) {
        return RegistryResponse.from(service.load(organizationId, scope, status, riskLevel,
                Boolean.TRUE.equals(attentionOnly), sort, limit));
    }

    @ExceptionHandler(MethodArgumentTypeMismatchException.class)
    @ResponseStatus(HttpStatus.BAD_REQUEST)
    public RequestController.ErrorResponse handleTypeMismatch(MethodArgumentTypeMismatchException e) {
        return new RequestController.ErrorResponse("Недопустимое значение параметра «" + e.getName()
                + "»: «" + e.getValue() + "»");
    }

    @ExceptionHandler(IllegalArgumentException.class)
    @ResponseStatus(HttpStatus.BAD_REQUEST)
    public RequestController.ErrorResponse handleBadRequest(IllegalArgumentException e) {
        return new RequestController.ErrorResponse(e.getMessage());
    }

    public record AttentionResponse(String code, String label) {
        static AttentionResponse from(AttentionFlag flag) {
            return new AttentionResponse(flag.name(), flag.label());
        }
    }

    public record SummaryResponse(int active, int completed, int scopeTotal, Map<String, Integer> byStatus,
                                  Map<String, Integer> byRiskLevel, Map<String, Integer> byAttention,
                                  int attentionTotal) {
        static SummaryResponse from(RequestRegistry.Summary summary) {
            return new SummaryResponse(summary.active(), summary.completed(), summary.scopeTotal(),
                    names(summary.byStatus()), names(summary.byRiskLevel()), names(summary.byAttention()),
                    summary.attentionTotal());
        }

        private static <K extends Enum<K>> Map<String, Integer> names(Map<K, Integer> source) {
            Map<String, Integer> result = new LinkedHashMap<>();
            source.forEach((key, value) -> result.put(key.name(), value));
            return result;
        }
    }

    public record RegistryRowResponse(UUID id, String routeCode, String routeName, String origin, String destination,
                                      LocalDate departureDate, String cargoDescription, int cargoValueCaps,
                                      Double etaHours, Integer riskScore, String riskStatus, String riskLevel,
                                      String riskLevelLabel, String recommendation, String status,
                                      String statusLabel, boolean terminal, OffsetDateTime lastStatusChangeAt,
                                      String lastStatusActorRole, String lastStatusActorRoleLabel,
                                      String lastStatusActorName, String lastStatusReason,
                                      List<AttentionResponse> attention, OffsetDateTime createdAt) {
        static RegistryRowResponse from(RegistryEntry entry) {
            ActorRole actorRole = entry.lastStatusActorRole();
            return new RegistryRowResponse(entry.id(), entry.routeCode(), entry.routeName(),
                    entry.origin(), entry.destination(), entry.departureDate(),
                    entry.cargoDescription(), entry.cargoValueCaps(), entry.etaHours(),
                    entry.riskScore(), entry.riskStatus(),
                    entry.riskLevel().name(),
                    entry.riskLevel().label(),
                    entry.recommendation(), entry.status().name(), entry.status().label(),
                    RequestStatusMachine.isTerminal(entry.status()), entry.lastStatusChangeAt(),
                    actorRole == null ? null : actorRole.name(),
                    actorRole == null ? null : actorRole.label(),
                    entry.lastStatusActorName(), entry.lastStatusReason(),
                    RequestRegistry.attentionFor(entry).stream().map(AttentionResponse::from).toList(),
                    entry.createdAt());
        }
    }

    public record RegistryResponse(UUID organizationId, String scope, String scopeLabel, String sort, int limit,
                                   int shown, boolean truncated, OffsetDateTime generatedAt,
                                   SummaryResponse summary, List<RegistryRowResponse> rows) {
        static RegistryResponse from(RegistryView view) {
            return new RegistryResponse(view.organizationId(), view.scope().name(), view.scope().label(),
                    view.sort().name(), view.limit(), view.shown(), view.truncated(), view.generatedAt(),
                    SummaryResponse.from(view.summary()),
                    view.rows().stream().map(RegistryRowResponse::from).toList());
        }
    }
}
