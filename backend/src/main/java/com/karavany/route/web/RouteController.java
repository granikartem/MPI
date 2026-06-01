package com.karavany.route.web;

import com.karavany.route.repository.RouteRepository;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;
import java.util.UUID;

@RestController
@RequestMapping("/api/routes")
public class RouteController {

    private final RouteRepository routeRepository;

    public RouteController(RouteRepository routeRepository) {
        this.routeRepository = routeRepository;
    }

    @GetMapping
    @Transactional(readOnly = true)
    public List<RouteOption> templates() {
        return routeRepository.findByTemplateTrue().stream()
                .map(r -> new RouteOption(r.getId(), r.getName()))
                .toList();
    }

    public record RouteOption(UUID id, String name) {
    }
}
