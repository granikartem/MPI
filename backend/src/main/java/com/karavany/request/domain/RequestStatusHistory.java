package com.karavany.request.domain;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.EnumType;
import jakarta.persistence.Enumerated;
import jakarta.persistence.FetchType;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.ManyToOne;
import jakarta.persistence.Table;

import java.time.OffsetDateTime;
import java.util.UUID;

@Entity
@Table(name = "request_status_history")
public class RequestStatusHistory {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private UUID id;

    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "request_id")
    private CaravanRequest request;

    @Enumerated(EnumType.STRING)
    @Column(name = "from_status")
    private RequestStatus fromStatus;

    @Enumerated(EnumType.STRING)
    @Column(name = "to_status", nullable = false)
    private RequestStatus toStatus;

    @Enumerated(EnumType.STRING)
    @Column(name = "actor_role", nullable = false)
    private ActorRole actorRole;

    @Column(name = "actor_name")
    private String actorName;

    private String reason;

    @Column(name = "occurred_at", nullable = false)
    private OffsetDateTime occurredAt = OffsetDateTime.now();

    protected RequestStatusHistory() {
    }

    public RequestStatusHistory(CaravanRequest request, RequestStatus fromStatus, RequestStatus toStatus,
                                ActorRole actorRole, String actorName, String reason) {
        this.request = request;
        this.fromStatus = fromStatus;
        this.toStatus = toStatus;
        this.actorRole = actorRole;
        this.actorName = actorName;
        this.reason = reason;
    }

    public UUID getId() {
        return id;
    }

    public CaravanRequest getRequest() {
        return request;
    }

    public RequestStatus getFromStatus() {
        return fromStatus;
    }

    public RequestStatus getToStatus() {
        return toStatus;
    }

    public ActorRole getActorRole() {
        return actorRole;
    }

    public String getActorName() {
        return actorName;
    }

    public String getReason() {
        return reason;
    }

    public OffsetDateTime getOccurredAt() {
        return occurredAt;
    }
}
