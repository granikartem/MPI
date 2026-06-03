package com.karavany.organization.repository;

import com.karavany.organization.domain.Organization;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

public interface OrganizationRepository extends JpaRepository<Organization, UUID> {

    List<Organization> findAllByOrderByCreatedAtDesc();

    Optional<Organization> findByNameIgnoreCase(String name);
}
