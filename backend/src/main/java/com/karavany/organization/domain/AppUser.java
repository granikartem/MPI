package com.karavany.organization.domain;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
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
@Table(name = "app_user")
public class AppUser {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private UUID id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "organization_id")
    private Organization organization;

    @Column(name = "full_name")
    private String fullName;

    private String login;

    @Column(name = "password_hash")
    private String passwordHash;

    private String role;

    @Column(name = "contact_channel")
    private String contactChannel;

    private boolean active = true;

    @Column(name = "created_at", updatable = false)
    private OffsetDateTime createdAt = OffsetDateTime.now();

    protected AppUser() {
    }

    public AppUser(Organization organization, String fullName, String login,
                   String passwordHash, String role, String contactChannel) {
        this.organization = organization;
        this.fullName = fullName;
        this.login = login;
        this.passwordHash = passwordHash;
        this.role = role;
        this.contactChannel = contactChannel;
    }

    public UUID getId() {
        return id;
    }

    public Organization getOrganization() {
        return organization;
    }

    public String getFullName() {
        return fullName;
    }

    public String getLogin() {
        return login;
    }

    public String getRole() {
        return role;
    }

    public String getContactChannel() {
        return contactChannel;
    }

    public boolean isActive() {
        return active;
    }

    public OffsetDateTime getCreatedAt() {
        return createdAt;
    }
}
