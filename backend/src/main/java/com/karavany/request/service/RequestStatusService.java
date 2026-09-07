package com.karavany.request.service;

import com.karavany.audit.AuditEvent;
import com.karavany.audit.AuditEventRepository;
import com.karavany.request.domain.ActorRole;
import com.karavany.request.domain.CaravanRequest;
import com.karavany.request.domain.RequestStatus;
import com.karavany.request.domain.RequestStatusHistory;
import com.karavany.request.domain.RequestStatusMachine;
import com.karavany.request.domain.RequestStatusMachine.Transition;
import com.karavany.request.repository.CaravanRequestRepository;
import com.karavany.request.repository.RequestStatusHistoryRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.Set;
import java.util.UUID;

@Service
public class RequestStatusService {

    private final CaravanRequestRepository requestRepository;
    private final RequestStatusHistoryRepository historyRepository;
    private final AuditEventRepository auditEventRepository;

    public RequestStatusService(CaravanRequestRepository requestRepository,
                                RequestStatusHistoryRepository historyRepository,
                                AuditEventRepository auditEventRepository) {
        this.requestRepository = requestRepository;
        this.historyRepository = historyRepository;
        this.auditEventRepository = auditEventRepository;
    }

    public record AvailableTransition(RequestStatus to, String action, Set<ActorRole> roles,
                                      boolean reasonRequired, String blockedReason) {
    }

    @Transactional
    public void recordCreation(CaravanRequest request) {
        historyRepository.save(new RequestStatusHistory(request, null, request.getStatus(),
                ActorRole.DISPATCHER, null, "Заявка создана"));
    }

    @Transactional(readOnly = true)
    public List<AvailableTransition> availableTransitions(CaravanRequest request) {
        return RequestStatusMachine.from(request.getStatus()).stream()
                .map(t -> new AvailableTransition(t.to(), t.action(), t.roles(), t.reasonRequired(),
                        RequestReadinessGuard.blockerFor(request, t.to())))
                .toList();
    }

    @Transactional(readOnly = true)
    public List<RequestStatusHistory> history(UUID requestId) {
        return historyRepository.findByRequest_IdOrderByOccurredAtAsc(requestId);
    }

    @Transactional
    public CaravanRequest changeStatus(CaravanRequest request, RequestStatus target, ActorRole actorRole,
                                       String actorName, String reason) {
        RequestStatus current = request.getStatus();
        if (current == target) {
            throw new StatusTransitionException("Заявка уже находится в статусе «" + target.label() + "»");
        }

        Transition transition = RequestStatusMachine.find(current, target)
                .orElseThrow(() -> new StatusTransitionException(
                        RequestStatusMachine.isTerminal(current)
                                ? "Статус «" + current.label() + "» финальный: переходы из него не предусмотрены"
                                : "Недопустимый переход: «" + current.label() + "» → «" + target.label() + "»"));

        if (!transition.roles().contains(actorRole)) {
            throw new StatusTransitionException("Роль «" + actorRole.label() + "» не может выполнить действие «"
                    + transition.action() + "». Разрешено: " + rolesLabel(transition.roles()));
        }

        String cleanReason = clean(reason);
        if (transition.reasonRequired() && cleanReason == null) {
            throw new StatusTransitionException("Для действия «" + transition.action() + "» нужно указать причину");
        }

        String blocked = RequestReadinessGuard.blockerFor(request, target);
        if (blocked != null) {
            throw new StatusTransitionException(blocked);
        }

        request.changeStatus(target);
        CaravanRequest saved = requestRepository.save(request);

        historyRepository.save(new RequestStatusHistory(saved, current, target, actorRole,
                clean(actorName), cleanReason));

        auditEventRepository.save(AuditEvent.requestStatusChanged(
                saved.getOrganization() == null ? null : saved.getOrganization().getId(),
                saved.getId(), current.name(), target.name(),
                actorRole.name(), clean(actorName), cleanReason));

        return saved;
    }

    private String rolesLabel(Set<ActorRole> roles) {
        return roles.stream().map(ActorRole::label).sorted().reduce((a, b) -> a + ", " + b).orElse("—");
    }

    private String clean(String value) {
        if (value == null || value.isBlank()) {
            return null;
        }
        return value.trim();
    }
}
