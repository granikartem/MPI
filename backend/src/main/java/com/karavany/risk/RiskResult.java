package com.karavany.risk;

import java.util.List;

/**
 * Результат расчёта risk_score с разбором слагаемых.
 * status: OK — актуально; STALE — данные старше 24 ч; NA — источник недоступен.
 * Формула: score = min(100, base + cargoFactor), где base = min(100, threatSum * 6).
 */
public record RiskResult(Integer score, String status, String recommendation, String asOf,
                         int threatSum, int base, int cargoFactor,
                         List<SegmentRisk> segments) {

    public record SegmentRisk(String segment, int threatLevel, List<String> threats) {
    }

    public static RiskResult unavailable() {
        return new RiskResult(null, "NA",
                "risk_score требует пересчёта — Wasteland Intel недоступен", null,
                0, 0, 0, List.of());
    }
}
