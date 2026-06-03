package com.karavany.audit;

import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.mapping.Document;

import java.time.Instant;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.UUID;

@Document("audit_event")
public class AuditEvent {

    @Id
    private String id;
    private String type;
    private String actor;
    private UUID organizationId;
    private UUID userId;
    private Map<String, Object> details;
    private Instant occurredAt;

    public AuditEvent() {
    }

    public AuditEvent(String type, String actor, UUID organizationId, UUID userId,
                      Map<String, Object> details, Instant occurredAt) {
        this.type = type;
        this.actor = actor;
        this.organizationId = organizationId;
        this.userId = userId;
        this.details = details;
        this.occurredAt = occurredAt;
    }

    public static AuditEvent organizationCreated(UUID organizationId, UUID dispatcherId,
                                                  String organizationName, String subscriptionTier,
                                                  String dispatcherLogin) {
        Map<String, Object> details = new LinkedHashMap<>();
        details.put("organizationName", organizationName);
        details.put("subscriptionTier", subscriptionTier);
        details.put("firstDispatcher", dispatcherLogin == null ? "SKIPPED" : dispatcherLogin);
        return new AuditEvent("ORGANIZATION_CREATED", "SUPERUSER", organizationId,
                dispatcherId, details, Instant.now());
    }

    public String getId() {
        return id;
    }

    public String getType() {
        return type;
    }

    public String getActor() {
        return actor;
    }

    public UUID getOrganizationId() {
        return organizationId;
    }

    public UUID getUserId() {
        return userId;
    }

    public Map<String, Object> getDetails() {
        return details;
    }

    public Instant getOccurredAt() {
        return occurredAt;
    }
}
