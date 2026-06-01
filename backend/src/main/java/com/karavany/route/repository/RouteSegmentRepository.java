package com.karavany.route.repository;

import com.karavany.route.domain.RouteSegment;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.UUID;

public interface RouteSegmentRepository extends JpaRepository<RouteSegment, UUID> {
}
