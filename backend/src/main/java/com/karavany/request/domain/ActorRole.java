package com.karavany.request.domain;

import java.util.Locale;

public enum ActorRole {

    DISPATCHER("Диспетчер караванов"),
    CARAVAN_MASTER("Караван-мастер"),
    SYSTEM("Система");

    private final String label;

    ActorRole(String label) {
        this.label = label;
    }

    public String label() {
        return label;
    }

    public static ActorRole parse(String value) {
        if (value == null || value.isBlank()) {
            throw new IllegalArgumentException("Не указана роль актора");
        }
        try {
            return valueOf(value.trim().toUpperCase(Locale.ROOT));
        } catch (IllegalArgumentException e) {
            throw new IllegalArgumentException("Неизвестная роль актора: " + value);
        }
    }
}
