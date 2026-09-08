package com.karavany.request.domain;

public enum AttentionFlag {

    DELAYED("Задержка"),
    AWAITING_CLOSURE("Ждёт закрытия"),
    RISK_RECALCULATION_REQUIRED("Требует пересчёта risk_score"),
    RISK_DATA_STALE("risk_score по устаревшим данным");

    private final String label;

    AttentionFlag(String label) {
        this.label = label;
    }

    public String label() {
        return label;
    }
}
