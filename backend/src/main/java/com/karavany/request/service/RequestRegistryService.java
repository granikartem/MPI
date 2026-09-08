package com.karavany.request.service;

import com.karavany.organization.repository.OrganizationRepository;
import com.karavany.request.domain.CaravanRequest;
import com.karavany.request.domain.RegistryEntry;
import com.karavany.request.domain.RegistryScope;
import com.karavany.request.domain.RegistrySort;
import com.karavany.request.domain.RequestRegistry;
import com.karavany.request.domain.RequestStatus;
import com.karavany.request.domain.RequestStatusHistory;
import com.karavany.request.repository.CaravanRequestRepository;
import com.karavany.request.repository.RequestStatusHistoryRepository;
import com.karavany.risk.RiskLevel;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.OffsetDateTime;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.UUID;

/** UC-3: сборка реестра рейсов организации — срез, отбор, сортировка и сводка. */
@Service
public class RequestRegistryService {

    private final CaravanRequestRepository requestRepository;
    private final RequestStatusHistoryRepository historyRepository;
    private final OrganizationRepository organizationRepository;

    public RequestRegistryService(CaravanRequestRepository requestRepository,
                                  RequestStatusHistoryRepository historyRepository,
                                  OrganizationRepository organizationRepository) {
        this.requestRepository = requestRepository;
        this.historyRepository = historyRepository;
        this.organizationRepository = organizationRepository;
    }

    public record RegistryView(UUID organizationId, RegistryScope scope, RegistrySort sort, int limit,
                               int shown, boolean truncated, OffsetDateTime generatedAt,
                               RequestRegistry.Summary summary, List<RegistryEntry> rows) {
    }

    @Transactional(readOnly = true)
    public RegistryView load(UUID organizationId, String scopeValue, List<String> statusValues,
                             List<String> riskLevelValues, boolean attentionOnly, String sortValue,
                             Integer limitValue) {
        if (organizationId == null) {
            throw new IllegalArgumentException("Не указана организация");
        }
        organizationRepository.findById(organizationId)
                .orElseThrow(() -> new IllegalArgumentException("Организация не найдена: «" + organizationId + "»"));

        RegistryScope scope = RegistryScope.parse(scopeValue);
        RegistrySort sort = RegistrySort.parse(sortValue);
        int limit = RequestRegistry.validateLimit(limitValue);
        Set<RequestStatus> statuses = RequestRegistry.parseStatuses(statusValues, scope);
        Set<RiskLevel> levels = RequestRegistry.parseRiskLevels(riskLevelValues);

        List<CaravanRequest> requests = requestRepository.findByOrganization_IdOrderByCreatedAtDesc(organizationId);
        Map<UUID, RequestStatusHistory> lastChanges = lastStatusChanges(requests);
        List<RegistryEntry> all = requests.stream()
                .map(request -> entry(request, lastChanges.get(request.getId())))
                .toList();
        List<RegistryEntry> scopeEntries = all.stream()
                .filter(entry -> scope.contains(entry.status()))
                .toList();

        int matchedCount = (int) scopeEntries.stream()
                .filter(entry -> RequestRegistry.matches(entry, statuses, levels, attentionOnly))
                .count();
        List<RegistryEntry> rows = RequestRegistry.rows(scopeEntries, statuses, levels, attentionOnly, sort, limit);

        return new RegistryView(organizationId, scope, sort, limit, rows.size(),
                RequestRegistry.truncated(matchedCount, limit), OffsetDateTime.now(),
                RequestRegistry.summarize(all, scope), rows);
    }

    private Map<UUID, RequestStatusHistory> lastStatusChanges(List<CaravanRequest> requests) {
        if (requests.isEmpty()) {
            return Map.of();
        }
        List<UUID> ids = requests.stream().map(CaravanRequest::getId).toList();
        Map<UUID, RequestStatusHistory> last = new HashMap<>();
        for (RequestStatusHistory history : historyRepository.findByRequest_IdInOrderByOccurredAtAsc(ids)) {
            last.put(history.getRequest().getId(), history);
        }
        return last;
    }

    private RegistryEntry entry(CaravanRequest request, RequestStatusHistory last) {
        return new RegistryEntry(request.getId(),
                request.getRoute() == null ? null : request.getRoute().getCode(),
                request.getRoute() == null ? null : request.getRoute().getName(),
                request.getOrigin(), request.getDestination(), request.getDepartureDate(),
                request.getCargoDescription(), request.getCargoValueCaps(), request.getEtaHours(),
                request.getRiskScore(), request.getRiskStatus(),
                RiskLevel.of(request.getRiskScore(), request.getRiskStatus()),
                request.getRecommendation(), request.getStatus(),
                last == null ? null : last.getOccurredAt(),
                last == null ? null : last.getActorRole(),
                last == null ? null : last.getActorName(),
                last == null ? null : last.getReason(),
                request.getCreatedAt());
    }
}
