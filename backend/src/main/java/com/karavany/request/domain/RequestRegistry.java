package com.karavany.request.domain;

import com.karavany.risk.RiskLevel;

import java.util.Collections;
import java.util.EnumSet;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;

public final class RequestRegistry {

    public static final int DEFAULT_LIMIT = 200;
    public static final int MAX_LIMIT = 1000;

    public record Summary(int active, int completed, int scopeTotal,
                          Map<RequestStatus, Integer> byStatus,
                          Map<RiskLevel, Integer> byRiskLevel,
                          Map<AttentionFlag, Integer> byAttention,
                          int attentionTotal) {
    }

    private RequestRegistry() {
    }

    public static Set<AttentionFlag> attentionFor(RegistryEntry entry) {
        EnumSet<AttentionFlag> flags = EnumSet.noneOf(AttentionFlag.class);
        if (entry.status() == RequestStatus.DELAYED) {
            flags.add(AttentionFlag.DELAYED);
        }
        if (entry.status() == RequestStatus.DELIVERED) {
            flags.add(AttentionFlag.AWAITING_CLOSURE);
        }
        if ("NA".equalsIgnoreCase(entry.riskStatus())) {
            flags.add(AttentionFlag.RISK_RECALCULATION_REQUIRED);
        }
        if ("STALE".equalsIgnoreCase(entry.riskStatus())) {
            flags.add(AttentionFlag.RISK_DATA_STALE);
        }
        return Collections.unmodifiableSet(flags);
    }

    public static boolean matches(RegistryEntry entry, Set<RequestStatus> statuses, Set<RiskLevel> levels,
                                  boolean attentionOnly) {
        if (statuses != null && !statuses.isEmpty() && !statuses.contains(entry.status())) {
            return false;
        }
        if (levels != null && !levels.isEmpty() && !levels.contains(entry.riskLevel())) {
            return false;
        }
        return !attentionOnly || !attentionFor(entry).isEmpty();
    }

    public static List<RegistryEntry> rows(List<RegistryEntry> scopeEntries, Set<RequestStatus> statuses,
                                          Set<RiskLevel> levels, boolean attentionOnly, RegistrySort sort,
                                          int limit) {
        return scopeEntries.stream()
                .filter(entry -> matches(entry, statuses, levels, attentionOnly))
                .sorted(sort.comparator())
                .limit(limit)
                .toList();
    }

    public static boolean truncated(int matchedCount, int limit) {
        return matchedCount > limit;
    }

    public static Summary summarize(List<RegistryEntry> all, RegistryScope scope) {
        Map<RequestStatus, Integer> byStatus = new LinkedHashMap<>();
        for (RequestStatus status : scope.statuses()) {
            byStatus.put(status, 0);
        }
        Map<RiskLevel, Integer> byRiskLevel = new LinkedHashMap<>();
        for (RiskLevel level : RiskLevel.values()) {
            byRiskLevel.put(level, 0);
        }
        Map<AttentionFlag, Integer> byAttention = new LinkedHashMap<>();
        for (AttentionFlag flag : AttentionFlag.values()) {
            byAttention.put(flag, 0);
        }

        int active = 0;
        int completed = 0;
        int attentionTotal = 0;
        for (RegistryEntry entry : all) {
            if (RegistryScope.ACTIVE.contains(entry.status())) {
                active++;
            } else {
                completed++;
            }
            if (!scope.contains(entry.status())) {
                continue;
            }
            byStatus.merge(entry.status(), 1, Integer::sum);
            byRiskLevel.merge(entry.riskLevel(), 1, Integer::sum);
            Set<AttentionFlag> flags = attentionFor(entry);
            for (AttentionFlag flag : flags) {
                byAttention.merge(flag, 1, Integer::sum);
            }
            if (!flags.isEmpty()) {
                attentionTotal++;
            }
        }

        int scopeTotal = scope == RegistryScope.COMPLETED ? completed : active;
        return new Summary(active, completed, scopeTotal,
                Collections.unmodifiableMap(byStatus),
                Collections.unmodifiableMap(byRiskLevel),
                Collections.unmodifiableMap(byAttention),
                attentionTotal);
    }

    public static int validateLimit(Integer limit) {
        if (limit == null) {
            return DEFAULT_LIMIT;
        }
        if (limit < 1 || limit > MAX_LIMIT) {
            throw new IllegalArgumentException("Недопустимый размер выборки: «" + limit
                    + "». Допустимо от 1 до " + MAX_LIMIT);
        }
        return limit;
    }

    public static Set<RequestStatus> parseStatuses(List<String> raw, RegistryScope scope) {
        EnumSet<RequestStatus> result = EnumSet.noneOf(RequestStatus.class);
        if (raw == null) {
            return Collections.unmodifiableSet(result);
        }
        for (String value : raw) {
            if (value == null || value.isBlank()) {
                continue;
            }
            RequestStatus status = RequestStatus.parse(value);
            if (!scope.contains(status)) {
                throw new IllegalArgumentException("Статус «" + status.label() + "» не входит в срез «"
                        + scope.label() + "»");
            }
            result.add(status);
        }
        return Collections.unmodifiableSet(result);
    }

    public static Set<RiskLevel> parseRiskLevels(List<String> raw) {
        EnumSet<RiskLevel> result = EnumSet.noneOf(RiskLevel.class);
        if (raw == null) {
            return Collections.unmodifiableSet(result);
        }
        for (String value : raw) {
            if (value == null || value.isBlank()) {
                continue;
            }
            result.add(RiskLevel.parse(value));
        }
        return Collections.unmodifiableSet(result);
    }
}
