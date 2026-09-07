package com.karavany.request.web;

import com.karavany.request.domain.ActorRole;
import com.karavany.request.domain.CaravanRequest;
import com.karavany.request.domain.RequestStatus;
import com.karavany.request.domain.RequestStatusHistory;
import com.karavany.request.domain.RequestStatusMachine;
import com.karavany.request.service.RequestService;
import com.karavany.request.service.RequestStatusService;
import com.karavany.request.service.RequestStatusService.AvailableTransition;
import com.karavany.request.service.StatusTransitionException;
import com.karavany.request.web.RequestController.RequestResponse;
import org.springframework.http.HttpStatus;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestController;

import java.time.OffsetDateTime;
import java.util.List;
import java.util.UUID;

@RestController
@RequestMapping("/api/requests/{id}")
public class RequestStatusController {

    private final RequestService requestService;
    private final RequestStatusService statusService;

    public RequestStatusController(RequestService requestService, RequestStatusService statusService) {
        this.requestService = requestService;
        this.statusService = statusService;
    }

    @GetMapping("/status")
    @Transactional(readOnly = true)
    public StatusInfoResponse status(@PathVariable UUID id) {
        CaravanRequest request = requestService.getById(id);
        return StatusInfoResponse.of(request, statusService.availableTransitions(request));
    }

    @PostMapping("/status")
    @Transactional
    public RequestResponse changeStatus(@PathVariable UUID id, @RequestBody ChangeStatusRequest body) {
        CaravanRequest request = requestService.getById(id);
        CaravanRequest updated = statusService.changeStatus(request,
                RequestStatus.parse(body.targetStatus()),
                ActorRole.parse(body.actorRole()),
                body.actorName(),
                body.reason());
        return RequestResponse.from(updated);
    }

    @GetMapping("/status-history")
    @Transactional(readOnly = true)
    public List<StatusHistoryResponse> history(@PathVariable UUID id) {
        requestService.getById(id);
        return statusService.history(id).stream().map(StatusHistoryResponse::from).toList();
    }

    @ExceptionHandler(StatusTransitionException.class)
    @ResponseStatus(HttpStatus.CONFLICT)
    public RequestController.ErrorResponse handleConflict(StatusTransitionException e) {
        return new RequestController.ErrorResponse(e.getMessage());
    }

    @ExceptionHandler(IllegalArgumentException.class)
    @ResponseStatus(HttpStatus.BAD_REQUEST)
    public RequestController.ErrorResponse handleBadRequest(IllegalArgumentException e) {
        return new RequestController.ErrorResponse(e.getMessage());
    }

    public record ChangeStatusRequest(String targetStatus, String actorRole, String actorName, String reason) {
    }

    public record TransitionResponse(String to, String toLabel, String action, List<String> roles,
                                     boolean reasonRequired, String blockedReason) {
        static TransitionResponse from(AvailableTransition t) {
            return new TransitionResponse(t.to().name(), t.to().label(), t.action(),
                    t.roles().stream().map(ActorRole::name).toList(),
                    t.reasonRequired(), t.blockedReason());
        }
    }

    public record StatusInfoResponse(UUID requestId, String status, String statusLabel, boolean terminal,
                                     List<TransitionResponse> transitions) {
        static StatusInfoResponse of(CaravanRequest request, List<AvailableTransition> transitions) {
            return new StatusInfoResponse(request.getId(), request.getStatus().name(),
                    request.getStatus().label(), RequestStatusMachine.isTerminal(request.getStatus()),
                    transitions.stream().map(TransitionResponse::from).toList());
        }
    }

    public record StatusHistoryResponse(UUID id, String fromStatus, String fromLabel, String toStatus,
                                        String toLabel, String actorRole, String actorRoleLabel,
                                        String actorName, String reason, OffsetDateTime occurredAt) {
        static StatusHistoryResponse from(RequestStatusHistory h) {
            return new StatusHistoryResponse(h.getId(),
                    h.getFromStatus() == null ? null : h.getFromStatus().name(),
                    h.getFromStatus() == null ? null : h.getFromStatus().label(),
                    h.getToStatus().name(), h.getToStatus().label(),
                    h.getActorRole().name(), h.getActorRole().label(),
                    h.getActorName(), h.getReason(), h.getOccurredAt());
        }
    }
}
