package com.karavany.request.domain;

import java.util.Collections;
import java.util.EnumSet;
import java.util.Locale;
import java.util.Set;

public enum RegistryScope {

    ACTIVE("Активные"),
    COMPLETED("Архив");

    private final String label;

    RegistryScope(String label) {
        this.label = label;
    }

    public String label() {
        return label;
    }

    public static RegistryScope parse(String value) {
        if (value == null || value.isBlank()) {
            return ACTIVE;
        }
        try {
            return valueOf(value.trim().toUpperCase(Locale.ROOT));
        } catch (IllegalArgumentException e) {
            throw new IllegalArgumentException("Неизвестный срез реестра: «" + value + "»");
        }
    }

    public boolean contains(RequestStatus status) {
        boolean terminal = RequestStatusMachine.isTerminal(status);
        return this == COMPLETED ? terminal : !terminal;
    }

    public Set<RequestStatus> statuses() {
        EnumSet<RequestStatus> result = EnumSet.noneOf(RequestStatus.class);
        for (RequestStatus status : RequestStatus.values()) {
            if (contains(status)) {
                result.add(status);
            }
        }
        return Collections.unmodifiableSet(result);
    }
}
