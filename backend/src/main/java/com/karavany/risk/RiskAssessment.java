package com.karavany.risk;

import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.mapping.Document;

import java.time.Instant;
import java.util.List;
import java.util.UUID;

/** Снимок оценки риска по заявке (хранится в MongoDB). */
@Document("risk_assessment")
public class RiskAssessment {

    @Id
    private String id;
    private UUID requestId;
    private Integer score;
    private String status;
    private String recommendation;
    private String asOf;
    private int threatSum;
    private int base;
    private int cargoFactor;
    private List<Segment> segments;
    private Instant computedAt;

    public RiskAssessment() {
    }

    public RiskAssessment(UUID requestId, RiskResult result, Instant computedAt) {
        this.requestId = requestId;
        this.score = result.score();
        this.status = result.status();
        this.recommendation = result.recommendation();
        this.asOf = result.asOf();
        this.threatSum = result.threatSum();
        this.base = result.base();
        this.cargoFactor = result.cargoFactor();
        this.segments = result.segments().stream()
                .map(s -> new Segment(s.segment(), s.threatLevel(), s.threats()))
                .toList();
        this.computedAt = computedAt;
    }

    public record Segment(String segment, int threatLevel, List<String> threats) {
    }

    public String getId() {
        return id;
    }

    public UUID getRequestId() {
        return requestId;
    }

    public Integer getScore() {
        return score;
    }

    public String getStatus() {
        return status;
    }

    public String getRecommendation() {
        return recommendation;
    }

    public String getAsOf() {
        return asOf;
    }

    public int getThreatSum() {
        return threatSum;
    }

    public int getBase() {
        return base;
    }

    public int getCargoFactor() {
        return cargoFactor;
    }

    public List<Segment> getSegments() {
        return segments;
    }

    public Instant getComputedAt() {
        return computedAt;
    }
}
