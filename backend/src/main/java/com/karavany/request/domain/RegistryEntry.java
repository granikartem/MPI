package com.karavany.request.domain;

import com.karavany.risk.RiskLevel;

import java.time.LocalDate;
import java.time.OffsetDateTime;
import java.util.UUID;

public record RegistryEntry(UUID id,
                            String routeCode,
                            String routeName,
                            String origin,
                            String destination,
                            LocalDate departureDate,
                            String cargoDescription,
                            int cargoValueCaps,
                            Double etaHours,
                            Integer riskScore,
                            String riskStatus,
                            RiskLevel riskLevel,
                            String recommendation,
                            RequestStatus status,
                            OffsetDateTime lastStatusChangeAt,
                            ActorRole lastStatusActorRole,
                            String lastStatusActorName,
                            String lastStatusReason,
                            OffsetDateTime createdAt) {
}
