package com.karavany.request.domain;

import com.karavany.risk.RiskLevel;

import java.time.LocalDate;
import java.time.OffsetDateTime;
import java.util.Comparator;
import java.util.Locale;
import java.util.UUID;

public enum RegistrySort {

    CREATED_DESC,
    DEPARTURE_ASC,
    RISK_DESC,
    STATUS_CHANGED_DESC;

    private static final Comparator<RegistryEntry> TIE_BREAK =
            Comparator.<RegistryEntry, OffsetDateTime>comparing(RegistryEntry::createdAt,
                            Comparator.nullsLast(Comparator.reverseOrder()))
                    .thenComparing(RegistryEntry::id, Comparator.nullsLast(Comparator.<UUID>naturalOrder()));

    public static RegistrySort parse(String value) {
        if (value == null || value.isBlank()) {
            return CREATED_DESC;
        }
        try {
            return valueOf(value.trim().toUpperCase(Locale.ROOT));
        } catch (IllegalArgumentException e) {
            throw new IllegalArgumentException("Неизвестный порядок сортировки реестра: «" + value + "»");
        }
    }

    public Comparator<RegistryEntry> comparator() {
        return switch (this) {
            case CREATED_DESC -> TIE_BREAK;
            case DEPARTURE_ASC -> Comparator.<RegistryEntry, LocalDate>comparing(RegistryEntry::departureDate,
                    Comparator.nullsLast(Comparator.naturalOrder())).thenComparing(TIE_BREAK);
            case RISK_DESC -> Comparator.<RegistryEntry, Boolean>comparing(
                            entry -> entry.riskLevel() == RiskLevel.UNKNOWN)
                    .thenComparing(RegistryEntry::riskScore, Comparator.nullsLast(Comparator.reverseOrder()))
                    .thenComparing(TIE_BREAK);
            case STATUS_CHANGED_DESC -> Comparator.<RegistryEntry, OffsetDateTime>comparing(
                    RegistryEntry::lastStatusChangeAt,
                    Comparator.nullsLast(Comparator.reverseOrder())).thenComparing(TIE_BREAK);
        };
    }
}
