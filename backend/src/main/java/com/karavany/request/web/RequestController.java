package com.karavany.request.web;

import com.karavany.request.domain.CaravanRequest;
import com.karavany.request.service.RequestService;
import com.karavany.request.service.RequestService.SegmentSpec;
import com.karavany.risk.RiskAssessment;
import org.springframework.http.HttpStatus;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestController;

import java.time.Instant;
import java.time.LocalDate;
import java.time.OffsetDateTime;
import java.util.List;
import java.util.UUID;

@RestController
@RequestMapping("/api/requests")
public class RequestController {

    private final RequestService service;

    public RequestController(RequestService service) {
        this.service = service;
    }

    @GetMapping
    @Transactional(readOnly = true)
    public List<RequestResponse> list(@RequestParam(required = false) UUID organizationId) {
        List<CaravanRequest> requests = organizationId == null
                ? service.findAll()
                : service.findByOrganization(organizationId);
        return requests.stream().map(RequestResponse::from).toList();
    }

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    @Transactional
    public RequestResponse create(@RequestBody CreateRequest body) {
        CaravanRequest created;
        if (body.routeId() != null) {
            created = service.create(body.organizationId(), body.origin(), body.destination(),
                    body.departureDate(), body.cargoDescription(), body.cargoValueCaps(), body.routeId());
        } else if (body.segments() != null && !body.segments().isEmpty()) {
            List<SegmentSpec> specs = body.segments().stream()
                    .map(s -> new SegmentSpec(s.fromCode(), s.toCode(), s.distanceKm()))
                    .toList();
            created = service.createWithManualRoute(body.organizationId(), body.origin(), body.destination(),
                    body.departureDate(), body.cargoDescription(), body.cargoValueCaps(), body.routeName(), specs);
        } else {
            throw new IllegalArgumentException("Нужно указать routeId (шаблон) или segments (ручной маршрут)");
        }
        return RequestResponse.from(created);
    }

    @PostMapping("/{id}/risk-score")
    @Transactional
    public RequestResponse recalculateRisk(@PathVariable UUID id) {
        return RequestResponse.from(service.recalculateRisk(id));
    }

    @DeleteMapping("/{id}/risk")
    @Transactional
    public RequestResponse clearRisk(@PathVariable UUID id) {
        return RequestResponse.from(service.clearRisk(id));
    }

    @GetMapping("/{id}/risk")
    @Transactional(readOnly = true)
    public RiskAssessmentResponse risk(@PathVariable UUID id) {
        RiskAssessment a = service.latestRiskAssessment(id)
                .orElseThrow(() -> new IllegalArgumentException("Оценка риска не найдена для заявки: " + id));
        List<SegmentRiskResponse> segments = a.getSegments().stream()
                .map(s -> new SegmentRiskResponse(s.segment(), s.threatLevel(), s.threats()))
                .toList();
        return new RiskAssessmentResponse(a.getRequestId(), a.getScore(), a.getStatus(),
                a.getRecommendation(), a.getAsOf(), a.getComputedAt(),
                a.getThreatSum(), a.getBase(), a.getCargoFactor(), segments);
    }

    @ExceptionHandler(IllegalArgumentException.class)
    @ResponseStatus(HttpStatus.BAD_REQUEST)
    public ErrorResponse handleBadRequest(IllegalArgumentException e) {
        return new ErrorResponse(e.getMessage());
    }

    public record CreateRequest(UUID organizationId, String origin, String destination, LocalDate departureDate,
                                String cargoDescription, int cargoValueCaps, UUID routeId,
                                String routeName, List<SegmentInput> segments) {
    }

    public record SegmentInput(String fromCode, String toCode, double distanceKm) {
    }

    public record RequestResponse(UUID id, UUID organizationId, String origin, String destination,
                                  LocalDate departureDate, String cargoDescription, int cargoValueCaps,
                                  String routeCode, String routeName, Double etaHours, Integer riskScore,
                                  String riskStatus, String recommendation, String status, String statusLabel,
                                  OffsetDateTime createdAt) {
        static RequestResponse from(CaravanRequest r) {
            return new RequestResponse(r.getId(),
                    r.getOrganization() != null ? r.getOrganization().getId() : null,
                    r.getOrigin(), r.getDestination(), r.getDepartureDate(),
                    r.getCargoDescription(), r.getCargoValueCaps(),
                    r.getRoute() != null ? r.getRoute().getCode() : null,
                    r.getRoute() != null ? r.getRoute().getName() : null,
                    r.getEtaHours(), r.getRiskScore(), r.getRiskStatus(), r.getRecommendation(),
                    r.getStatus().name(), r.getStatus().label(), r.getCreatedAt());
        }
    }

    public record SegmentRiskResponse(String segment, int threatLevel, List<String> threats) {
    }

    public record RiskAssessmentResponse(UUID requestId, Integer score, String status, String recommendation,
                                         String asOf, Instant computedAt, int threatSum, int base,
                                         int cargoFactor, List<SegmentRiskResponse> segments) {
    }

    public record ErrorResponse(String message) {
    }
}
