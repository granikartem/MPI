package com.karavany.request.service;

import com.karavany.request.domain.CaravanRequest;
import com.karavany.request.repository.CaravanRequestRepository;
import com.karavany.risk.RiskAssessment;
import com.karavany.risk.RiskResult;
import com.karavany.risk.RiskService;
import com.karavany.route.domain.Checkpoint;
import com.karavany.route.domain.Route;
import com.karavany.route.domain.RouteSegment;
import com.karavany.route.repository.CheckpointRepository;
import com.karavany.route.repository.RouteRepository;
import com.karavany.route.repository.RouteSegmentRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDate;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

/** UC-1: создание и сопровождение заявки на перевозку. */
@Service
public class RequestService {

    private final CaravanRequestRepository requestRepository;
    private final RouteRepository routeRepository;
    private final RouteSegmentRepository routeSegmentRepository;
    private final CheckpointRepository checkpointRepository;
    private final EtaService etaService;
    private final RiskService riskService;

    public RequestService(CaravanRequestRepository requestRepository, RouteRepository routeRepository,
                          RouteSegmentRepository routeSegmentRepository, CheckpointRepository checkpointRepository,
                          EtaService etaService, RiskService riskService) {
        this.requestRepository = requestRepository;
        this.routeRepository = routeRepository;
        this.routeSegmentRepository = routeSegmentRepository;
        this.checkpointRepository = checkpointRepository;
        this.etaService = etaService;
        this.riskService = riskService;
    }

    public record SegmentSpec(String fromCode, String toCode, double distanceKm) {
    }

    @Transactional(readOnly = true)
    public List<CaravanRequest> findAll() {
        return requestRepository.findAllByOrderByCreatedAtDesc();
    }

    @Transactional(readOnly = true)
    public CaravanRequest getById(UUID id) {
        return requestRepository.findById(id)
                .orElseThrow(() -> new IllegalArgumentException("Заявка не найдена: " + id));
    }

    /** Основной поток: маршрут выбран из шаблона. */
    @Transactional
    public CaravanRequest create(String origin, String destination, LocalDate departureDate,
                                 String cargoDescription, int cargoValueCaps, UUID routeId) {
        Route route = routeRepository.findById(routeId)
                .orElseThrow(() -> new IllegalArgumentException("Маршрут не найден: " + routeId));
        return build(origin, destination, departureDate, cargoDescription, cargoValueCaps, route);
    }

    /** Альт. поток 3а: маршрут задан вручную последовательностью участков. */
    @Transactional
    public CaravanRequest createWithManualRoute(String origin, String destination, LocalDate departureDate,
                                                String cargoDescription, int cargoValueCaps,
                                                List<SegmentSpec> specs) {
        if (specs == null || specs.isEmpty()) {
            throw new IllegalArgumentException("Ручной маршрут должен содержать хотя бы один участок");
        }
        Route route = routeRepository.save(new Route("Ручной маршрут: " + origin + " → " + destination, false));

        List<RouteSegment> segments = new ArrayList<>();
        int ord = 1;
        for (SegmentSpec spec : specs) {
            Checkpoint from = checkpointRepository.findByCode(spec.fromCode())
                    .orElseThrow(() -> new IllegalArgumentException("Контрольная точка не найдена: " + spec.fromCode()));
            Checkpoint to = checkpointRepository.findByCode(spec.toCode())
                    .orElseThrow(() -> new IllegalArgumentException("Контрольная точка не найдена: " + spec.toCode()));
            segments.add(new RouteSegment(route, ord++, from, to, spec.distanceKm()));
        }
        routeSegmentRepository.saveAll(segments);
        route.getSegments().addAll(segments);

        return build(origin, destination, departureDate, cargoDescription, cargoValueCaps, route);
    }

    @Transactional
    public CaravanRequest recalculateRisk(UUID id) {
        CaravanRequest request = getById(id);
        RiskResult risk = riskService.calculate(request.getRoute(), request.getCargoValueCaps());
        request.applyRisk(risk.score(), risk.status(), risk.recommendation());
        CaravanRequest saved = requestRepository.save(request);
        riskService.saveAssessment(saved.getId(), risk);
        return saved;
    }

    @Transactional(readOnly = true)
    public Optional<RiskAssessment> latestRiskAssessment(UUID id) {
        return riskService.latestAssessment(id);
    }

    /** Сброс оценки риска: удаляет снимки из Mongo и обнуляет risk_score заявки (статус NA). */
    @Transactional
    public CaravanRequest clearRisk(UUID id) {
        CaravanRequest request = getById(id);
        riskService.deleteAssessments(id);
        request.applyRisk(null, "NA", null);
        return requestRepository.save(request);
    }

    private CaravanRequest build(String origin, String destination, LocalDate departureDate,
                                 String cargoDescription, int cargoValueCaps, Route route) {
        CaravanRequest request = new CaravanRequest(origin, destination, departureDate,
                cargoDescription, cargoValueCaps, route);

        // FR-5: ETA по маршруту
        request.applyEta(etaService.computeHours(route));

        // UC-7: risk_score (с fallback при недоступности Wasteland Intel)
        RiskResult risk = riskService.calculate(route, cargoValueCaps);
        request.applyRisk(risk.score(), risk.status(), risk.recommendation());

        CaravanRequest saved = requestRepository.save(request);
        riskService.saveAssessment(saved.getId(), risk);
        return saved;
    }
}
