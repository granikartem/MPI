package com.karavany.risk;

import java.util.Locale;

public enum RiskLevel {

    UNKNOWN("Н/Д"),
    LOW("Низкий"),
    MEDIUM("Средний"),
    HIGH("Высокий"),
    CRITICAL("Критический");

    private final String label;

    RiskLevel(String label) {
        this.label = label;
    }

    public String label() {
        return label;
    }

    public static RiskLevel parse(String value) {
        if (value == null || value.isBlank()) {
            throw new IllegalArgumentException("Не указан уровень риска");
        }
        try {
            return valueOf(value.trim().toUpperCase(Locale.ROOT));
        } catch (IllegalArgumentException e) {
            throw new IllegalArgumentException("Неизвестный уровень риска: «" + value + "»");
        }
    }

    public static RiskLevel of(Integer score, String riskStatus) {
        if ("NA".equalsIgnoreCase(riskStatus) || score == null) {
            return UNKNOWN;
        }
        if (score >= 80) {
            return CRITICAL;
        }
        if (score >= 60) {
            return HIGH;
        }
        if (score >= 30) {
            return MEDIUM;
        }
        return LOW;
    }
}
