package com.karavany.request.repository;

import com.karavany.request.domain.CaravanRequest;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;
import java.util.UUID;

public interface CaravanRequestRepository extends JpaRepository<CaravanRequest, UUID> {

    List<CaravanRequest> findAllByOrderByCreatedAtDesc();
}
