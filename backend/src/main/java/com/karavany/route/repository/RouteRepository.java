package com.karavany.route.repository;

import com.karavany.route.domain.Route;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;
import java.util.UUID;

public interface RouteRepository extends JpaRepository<Route, UUID> {

    List<Route> findByTemplateTrue();
}
