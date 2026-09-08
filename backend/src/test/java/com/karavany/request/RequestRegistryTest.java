package com.karavany.request;

import com.karavany.request.domain.ActorRole;
import com.karavany.request.domain.AttentionFlag;
import com.karavany.request.domain.RegistryEntry;
import com.karavany.request.domain.RegistryScope;
import com.karavany.request.domain.RegistrySort;
import com.karavany.request.domain.RequestRegistry;
import com.karavany.request.domain.RequestStatus;
import com.karavany.request.domain.RequestStatusMachine;
import com.karavany.risk.RiskLevel;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import java.nio.charset.StandardCharsets;
import java.time.LocalDate;
import java.time.OffsetDateTime;
import java.util.ArrayList;
import java.util.EnumSet;
import java.util.List;
import java.util.Set;
import java.util.UUID;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

class RequestRegistryTest {

    private static final OffsetDateTime BASE = OffsetDateTime.parse("2287-10-20T08:00:00Z");

    @Test
    @DisplayName("Срез «Активные» — все нефинальные статусы, включая «Доставлен»")
    void activeScopeHoldsAllNonTerminalStatuses() {
        assertEquals(EnumSet.of(RequestStatus.DRAFT, RequestStatus.READY, RequestStatus.EN_ROUTE,
                RequestStatus.DELAYED, RequestStatus.DELIVERED), RegistryScope.ACTIVE.statuses());
        assertTrue(RegistryScope.ACTIVE.contains(RequestStatus.DELIVERED));
        assertFalse(RegistryScope.ACTIVE.contains(RequestStatus.CLOSED));
        assertEquals("Активные", RegistryScope.ACTIVE.label());
    }

    @Test
    @DisplayName("Срез «Архив» — ровно финальные статусы «Закрыт» и «Отменён»")
    void completedScopeHoldsExactlyTerminalStatuses() {
        assertEquals(EnumSet.of(RequestStatus.CLOSED, RequestStatus.CANCELLED),
                RegistryScope.COMPLETED.statuses());
        for (RequestStatus status : RequestStatus.values()) {
            assertEquals(RequestStatusMachine.isTerminal(status), RegistryScope.COMPLETED.contains(status),
                    "срез «Архив» разошёлся со статусной моделью на " + status);
        }
        assertEquals("Архив", RegistryScope.COMPLETED.label());
    }

    @Test
    @DisplayName("Срезы покрывают все семь статусов без пересечений")
    void scopesPartitionAllStatuses() {
        EnumSet<RequestStatus> union = EnumSet.copyOf(RegistryScope.ACTIVE.statuses());
        union.addAll(RegistryScope.COMPLETED.statuses());
        assertEquals(RequestStatus.values().length, union.size());

        EnumSet<RequestStatus> intersection = EnumSet.copyOf(RegistryScope.ACTIVE.statuses());
        intersection.retainAll(RegistryScope.COMPLETED.statuses());
        assertTrue(intersection.isEmpty());
    }

    @Test
    @DisplayName("Уровни риска определяются порогами 30, 60 и 80")
    void riskLevelThresholds() {
        assertEquals(RiskLevel.LOW, RiskLevel.of(0, "OK"));
        assertEquals(RiskLevel.LOW, RiskLevel.of(29, "OK"));
        assertEquals(RiskLevel.MEDIUM, RiskLevel.of(30, "OK"));
        assertEquals(RiskLevel.MEDIUM, RiskLevel.of(59, "OK"));
        assertEquals(RiskLevel.HIGH, RiskLevel.of(60, "OK"));
        assertEquals(RiskLevel.HIGH, RiskLevel.of(79, "OK"));
        assertEquals(RiskLevel.CRITICAL, RiskLevel.of(80, "OK"));
        assertEquals(RiskLevel.CRITICAL, RiskLevel.of(100, "OK"));
        assertEquals("Средний", RiskLevel.MEDIUM.label());
    }

    @Test
    @DisplayName("Статус оценки «NA» даёт «Н/Д» независимо от значения risk_score")
    void notAssessedRiskIsAlwaysUnknown() {
        assertEquals(RiskLevel.UNKNOWN, RiskLevel.of(95, "NA"));
        assertEquals(RiskLevel.UNKNOWN, RiskLevel.of(0, "NA"));
        assertEquals(RiskLevel.UNKNOWN, RiskLevel.of(null, "OK"));
        assertEquals("Н/Д", RiskLevel.UNKNOWN.label());
    }

    @Test
    @DisplayName("Флаги «Задержка» и «Ждёт закрытия» выставляются по статусу рейса")
    void statusDrivenAttentionFlags() {
        assertEquals(Set.of(AttentionFlag.DELAYED),
                RequestRegistry.attentionFor(entry("RT-1", RequestStatus.DELAYED, 40, "OK", 0)));
        assertEquals(Set.of(AttentionFlag.AWAITING_CLOSURE),
                RequestRegistry.attentionFor(entry("RT-2", RequestStatus.DELIVERED, 40, "OK", 0)));
        assertTrue(RequestRegistry.attentionFor(entry("RT-3", RequestStatus.EN_ROUTE, 40, "OK", 0)).isEmpty());
    }

    @Test
    @DisplayName("Флаги «требует пересчёта» и «устаревшие данные» выставляются по статусу оценки риска")
    void riskStatusDrivenAttentionFlags() {
        assertEquals(Set.of(AttentionFlag.RISK_RECALCULATION_REQUIRED),
                RequestRegistry.attentionFor(entry("RT-1", RequestStatus.DRAFT, null, "NA", 0)));
        assertEquals(Set.of(AttentionFlag.RISK_DATA_STALE),
                RequestRegistry.attentionFor(entry("RT-2", RequestStatus.EN_ROUTE, 40, "STALE", 0)));
        assertEquals(Set.of(AttentionFlag.AWAITING_CLOSURE, AttentionFlag.RISK_DATA_STALE),
                RequestRegistry.attentionFor(entry("RT-3", RequestStatus.DELIVERED, 40, "STALE", 0)));
    }

    @Test
    @DisplayName("Критический уровень риска сам по себе флагом внимания не является")
    void criticalRiskIsNotAnAttentionFlag() {
        RegistryEntry critical = entry("RT-1", RequestStatus.EN_ROUTE, 95, "OK", 0);
        assertEquals(RiskLevel.CRITICAL, critical.riskLevel());
        assertTrue(RequestRegistry.attentionFor(critical).isEmpty());
    }

    @Test
    @DisplayName("Отбор «только требующие внимания» возвращает ровно столько строк, сколько в сводке")
    void attentionOnlyMatchesSummary() {
        List<RegistryEntry> all = sample();
        RequestRegistry.Summary summary = RequestRegistry.summarize(all, RegistryScope.ACTIVE);
        List<RegistryEntry> rows = RequestRegistry.rows(scope(all, RegistryScope.ACTIVE), Set.of(), Set.of(),
                true, RegistrySort.CREATED_DESC, RequestRegistry.DEFAULT_LIMIT);

        assertEquals(3, summary.attentionTotal());
        assertEquals(summary.attentionTotal(), rows.size());
        assertEquals(List.of("RT-4", "RT-3", "RT-1"), codes(rows));
    }

    @Test
    @DisplayName("Фильтры по статусу и уровню риска не меняют сводку по срезу")
    void filtersDoNotChangeSummary() {
        List<RegistryEntry> all = sample();
        RequestRegistry.Summary summary = RequestRegistry.summarize(all, RegistryScope.ACTIVE);
        List<RegistryEntry> filtered = RequestRegistry.rows(scope(all, RegistryScope.ACTIVE),
                Set.of(RequestStatus.EN_ROUTE), Set.of(RiskLevel.MEDIUM), false,
                RegistrySort.CREATED_DESC, RequestRegistry.DEFAULT_LIMIT);

        assertEquals(List.of("RT-2"), codes(filtered));
        assertEquals(5, summary.active());
        assertEquals(2, summary.completed());
        assertEquals(5, summary.scopeTotal());
        assertEquals(1, summary.byStatus().get(RequestStatus.DELIVERED));
        assertEquals(1, summary.byRiskLevel().get(RiskLevel.CRITICAL));
        assertEquals(1, summary.byAttention().get(AttentionFlag.RISK_DATA_STALE));
        assertEquals(3, summary.attentionTotal());

        RequestRegistry.Summary ofFiltered = RequestRegistry.summarize(filtered, RegistryScope.ACTIVE);
        assertNotEquals(summary, ofFiltered,
                "сводка обязана считаться по срезу, а не по отфильтрованной выборке");
        assertEquals(1, ofFiltered.scopeTotal());
        assertEquals(0, ofFiltered.attentionTotal());

        List<RegistryEntry> limited = RequestRegistry.rows(scope(all, RegistryScope.ACTIVE),
                Set.of(), Set.of(), false, RegistrySort.CREATED_DESC, 1);
        assertEquals(1, limited.size());
        assertEquals(summary, RequestRegistry.summarize(all, RegistryScope.ACTIVE),
                "ограничение выборки не влияет на сводку");
    }

    @Test
    @DisplayName("Сортировка по risk_score ставит рейсы без оценки в конец списка")
    void riskSortPutsUnknownLast() {
        List<RegistryEntry> rows = RequestRegistry.rows(scope(sample(), RegistryScope.ACTIVE), Set.of(), Set.of(),
                false, RegistrySort.RISK_DESC, RequestRegistry.DEFAULT_LIMIT);

        List<Integer> scores = new ArrayList<>();
        rows.forEach(row -> scores.add(row.riskScore()));
        assertEquals(List.of(95, 62, 45, 20), scores.subList(0, 4));
        assertEquals(5, scores.size());
        assertNull(rows.get(4).riskScore());
        assertEquals(RiskLevel.UNKNOWN, rows.get(4).riskLevel());

        List<RegistryEntry> withStaleScore = List.of(
                entry("RT-8", RequestStatus.EN_ROUTE, 90, "NA", 7),
                entry("RT-9", RequestStatus.EN_ROUTE, 50, "OK", 8));
        List<RegistryEntry> sorted = RequestRegistry.rows(withStaleScore, Set.of(), Set.of(), false,
                RegistrySort.RISK_DESC, RequestRegistry.DEFAULT_LIMIT);
        assertEquals(List.of("RT-9", "RT-8"), codes(sorted),
                "рейс с «Н/Д» уходит в конец даже при сохранённом значении risk_score");
    }

    @Test
    @DisplayName("Сортировка по умолчанию — сначала новые")
    void defaultSortIsNewestFirst() {
        List<RegistryEntry> rows = RequestRegistry.rows(scope(sample(), RegistryScope.ACTIVE), Set.of(), Set.of(),
                false, RegistrySort.parse(null), RequestRegistry.DEFAULT_LIMIT);

        assertEquals(RegistrySort.CREATED_DESC, RegistrySort.parse(null));
        assertEquals(List.of("RT-5", "RT-4", "RT-3", "RT-2", "RT-1"), codes(rows));
    }

    @Test
    @DisplayName("Пустой реестр: все ключи сводки присутствуют и равны нулю")
    void emptyRegistryKeepsAllSummaryKeys() {
        RequestRegistry.Summary summary = RequestRegistry.summarize(List.of(), RegistryScope.ACTIVE);

        assertEquals(0, summary.active());
        assertEquals(0, summary.completed());
        assertEquals(0, summary.scopeTotal());
        assertEquals(0, summary.attentionTotal());
        assertEquals(RegistryScope.ACTIVE.statuses(), summary.byStatus().keySet());
        assertEquals(5, summary.byRiskLevel().size());
        assertEquals(4, summary.byAttention().size());
        summary.byStatus().values().forEach(value -> assertEquals(0, value));
        summary.byRiskLevel().values().forEach(value -> assertEquals(0, value));
        summary.byAttention().values().forEach(value -> assertEquals(0, value));
    }

    @Test
    @DisplayName("Ограничение выборки усекает список и выставляет признак усечения")
    void limitTruncatesRows() {
        List<RegistryEntry> scopeEntries = scope(sample(), RegistryScope.ACTIVE);
        List<RegistryEntry> rows = RequestRegistry.rows(scopeEntries, Set.of(), Set.of(), false,
                RegistrySort.CREATED_DESC, 2);

        assertEquals(List.of("RT-5", "RT-4"), codes(rows));
        assertTrue(RequestRegistry.truncated(scopeEntries.size(), 2));
        assertFalse(RequestRegistry.truncated(scopeEntries.size(), RequestRegistry.DEFAULT_LIMIT));
        assertEquals(RequestRegistry.DEFAULT_LIMIT, RequestRegistry.validateLimit(null));
    }

    @Test
    @DisplayName("Размер выборки вне диапазона и статус не из среза отклоняются")
    void invalidQueryParametersAreRejected() {
        assertTrue(assertThrows(IllegalArgumentException.class, () -> RequestRegistry.validateLimit(0))
                .getMessage().contains("Допустимо от 1 до 1000"));
        assertThrows(IllegalArgumentException.class, () -> RequestRegistry.validateLimit(1001));

        String message = assertThrows(IllegalArgumentException.class,
                () -> RequestRegistry.parseStatuses(List.of("CLOSED"), RegistryScope.ACTIVE)).getMessage();
        assertEquals("Статус «Закрыт» не входит в срез «Активные»", message);

        assertThrows(IllegalArgumentException.class, () -> RequestRegistry.parseRiskLevels(List.of("EXTREME")));
        assertThrows(IllegalArgumentException.class, () -> RegistryScope.parse("ALL"));
        assertThrows(IllegalArgumentException.class, () -> RegistrySort.parse("PRICE_ASC"));
    }

    private static List<RegistryEntry> sample() {
        return List.of(
                entry("RT-1", RequestStatus.DRAFT, null, "NA", 0),
                entry("RT-2", RequestStatus.EN_ROUTE, 45, "OK", 1),
                entry("RT-3", RequestStatus.DELAYED, 62, "OK", 2),
                entry("RT-4", RequestStatus.DELIVERED, 20, "STALE", 3),
                entry("RT-5", RequestStatus.READY, 95, "OK", 4),
                entry("RT-6", RequestStatus.CLOSED, 15, "OK", 5),
                entry("RT-7", RequestStatus.CANCELLED, null, "NA", 6));
    }

    private static List<RegistryEntry> scope(List<RegistryEntry> all, RegistryScope scope) {
        return all.stream().filter(entry -> scope.contains(entry.status())).toList();
    }

    private static List<String> codes(List<RegistryEntry> rows) {
        return rows.stream().map(RegistryEntry::routeCode).toList();
    }

    private static RegistryEntry entry(String routeCode, RequestStatus status, Integer riskScore,
                                       String riskStatus, int createdShiftHours) {
        return new RegistryEntry(UUID.nameUUIDFromBytes(routeCode.getBytes(StandardCharsets.UTF_8)),
                routeCode, "Маршрут " + routeCode, "Goodsprings", "New Vegas",
                LocalDate.parse("2287-10-25"), "Медикаменты", 5000, 47.5,
                riskScore, riskStatus, RiskLevel.of(riskScore, riskStatus), null, status,
                BASE.plusHours(createdShiftHours), ActorRole.DISPATCHER, "Кэсседи", null,
                BASE.plusHours(createdShiftHours));
    }
}
