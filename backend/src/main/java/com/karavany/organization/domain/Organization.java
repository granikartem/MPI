package com.karavany.organization.domain;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

import java.time.OffsetDateTime;
import java.util.UUID;

@Entity
@Table(name = "organization")
public class Organization {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private UUID id;

    @Column(name = "tenant_key")
    private String tenantKey;

    private String name;

    @Column(name = "subscription_tier")
    private String subscriptionTier;

    @Column(name = "legal_address")
    private String legalAddress;

    @Column(name = "primary_contact")
    private String primaryContact;

    @Column(name = "contact_channel")
    private String contactChannel;

    private String region;
    private String status = "ACTIVE";

    @Column(name = "created_at", updatable = false)
    private OffsetDateTime createdAt = OffsetDateTime.now();

    protected Organization() {
    }

    public Organization(String tenantKey, String name, String subscriptionTier,
                        String legalAddress, String primaryContact,
                        String contactChannel, String region) {
        this.tenantKey = tenantKey;
        this.name = name;
        this.subscriptionTier = subscriptionTier;
        this.legalAddress = legalAddress;
        this.primaryContact = primaryContact;
        this.contactChannel = contactChannel;
        this.region = region;
    }

    public UUID getId() {
        return id;
    }

    public String getTenantKey() {
        return tenantKey;
    }

    public String getName() {
        return name;
    }

    public String getSubscriptionTier() {
        return subscriptionTier;
    }

    public String getLegalAddress() {
        return legalAddress;
    }

    public String getPrimaryContact() {
        return primaryContact;
    }

    public String getContactChannel() {
        return contactChannel;
    }

    public String getRegion() {
        return region;
    }

    public String getStatus() {
        return status;
    }

    public OffsetDateTime getCreatedAt() {
        return createdAt;
    }
}
