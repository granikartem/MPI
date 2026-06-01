package com.karavany.risk;

import com.karavany.risk.WastelandIntelClient.SegmentThreat;
import com.karavany.risk.WastelandIntelClient.ThreatReport;
import com.karavany.route.domain.Route;
import com.karavany.route.domain.RouteSegment;
import org.springframework.stereotype.Service;

import java.time.Instant;
import java.time.OffsetDateTime;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.stream.Collectors;

/**
 * UC-7: расчёт risk_score маршрута на основе данных Wasteland Intel и ценности груза.
 */
@Service
public class RiskService {

    private final WastelandIntelClient intelClient;
    private final RiskAssessmentRepository assessmentRepository;

    public RiskService(WastelandIntelClient intelClient, RiskAssessmentRepository assessmentRepository) {
        this.intelClient = intelClient;
        this.assessmentRepository = assessmentRepository;
    }

    public RiskResult calculate(Route route, int cargoValueCaps) {
        List<String> keys = route.getSegments().stream()
                .map(RouteSegment::segmentKey)
                .toList();

        Optional<ThreatReport> maybeReport = intelClient.fetchThreats(keys);
        if (maybeReport.isEmpty()) {
            return RiskResult.unavailable();
        }
        ThreatReport report = maybeReport.get();

        Map<String, SegmentThreat> byKey = report.segments() == null ? Map.of()
                : report.segments().stream()
                .collect(Collectors.toMap(SegmentThreat::segment, s -> s, (a, b) -> a));

        List<RiskResult.SegmentRisk> segments = keys.stream()
                .map(k -> {
                    SegmentThreat t = byKey.get(k);
                    return t == null
                            ? new RiskResult.SegmentRisk(k, 0, List.of())
                            : new RiskResult.SegmentRisk(k, t.threatLevel(),
                            t.threats() == null ? List.of() : t.threats());
                })
                .toList();

        int threatSum = segments.stream().mapToInt(RiskResult.SegmentRisk::threatLevel).sum();
        int base = Math.min(100, threatSum * 6);
        int cargoFactor = cargoFactor(cargoValueCaps);
        int score = Math.min(100, base + cargoFactor);

        String status = isStale(report.asOf()) ? "STALE" : "OK";
        return new RiskResult(score, status, recommendation(score), report.asOf(),
                threatSum, base, cargoFactor, segments);
    }

    /** Сохраняет снимок оценки риска в MongoDB. */
    public void saveAssessment(java.util.UUID requestId, RiskResult result) {
        assessmentRepository.save(new RiskAssessment(requestId, result, Instant.now()));
    }

    public Optional<RiskAssessment> latestAssessment(java.util.UUID requestId) {
        return assessmentRepository.findFirstByRequestIdOrderByComputedAtDesc(requestId);
    }

    /** Удаляет все снимки оценки риска по заявке. */
    public void deleteAssessments(java.util.UUID requestId) {
        assessmentRepository.deleteByRequestId(requestId);
    }

    private int cargoFactor(int caps) {
        if (caps >= 20_000) return 30;
        if (caps >= 5_000) return 20;
        if (caps >= 1_000) return 10;
        return 0;
    }

    private boolean isStale(String asOf) {
        if (asOf == null || asOf.isBlank()) {
            return false;
        }
        try {
            return OffsetDateTime.parse(asOf).isBefore(OffsetDateTime.now().minusHours(24));
        } catch (Exception e) {
            return false;
        }
    }

    private String recommendation(int score) {
        if (score >= 80) return "Критический риск: охрана ≥8, медик обязателен, удвоенные припасы";
        if (score >= 60) return "Высокий риск: охрана ≥6, усиленные припасы";
        if (score >= 30) return "Средний риск: охрана ≥4, стандартные припасы";
        return "Низкий риск: охрана ≥2, базовые припасы";
    }
}
