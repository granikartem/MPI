package com.karavany.route.repository;

import com.karavany.route.domain.Checkpoint;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;
import java.util.UUID;

public interface CheckpointRepository extends JpaRepository<Checkpoint, UUID> {

    Optional<Checkpoint> findByCode(String code);
}
