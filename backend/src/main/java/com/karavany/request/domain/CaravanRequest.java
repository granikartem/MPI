package com.karavany.request.domain;

import com.karavany.route.domain.Route;
import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.FetchType;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.ManyToOne;
import jakarta.persistence.Table;

import java.time.LocalDate;
import java.time.OffsetDateTime;
import java.util.UUID;

@Entity
@Table(name = "caravan_request")
public class CaravanRequest {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private UUID id;

    private String origin;
    private String destination;

    @Column(name = "departure_date")
    private LocalDate departureDate;

    @Column(name = "cargo_description")
    private String cargoDescription;

    @Column(name = "cargo_value_caps")
    private int cargoValueCaps;

    @ManyToOne(fetch = FetchType.EAGER)
    @JoinColumn(name = "route_id")
    private Route route;

    @Column(name = "eta_hours")
    private Double etaHours;

    @Column(name = "risk_score")
    private Integer riskScore;

    @Column(name = "risk_status")
    private String riskStatus = "NA";

    private String recommendation;

    private String status = "DRAFT";

    @Column(name = "created_at", insertable = false, updatable = false)
    private OffsetDateTime createdAt;

    protected CaravanRequest() {
    }

    public CaravanRequest(String origin, String destination, LocalDate departureDate,
                          String cargoDescription, int cargoValueCaps, Route route) {
        this.origin = origin;
        this.destination = destination;
        this.departureDate = departureDate;
        this.cargoDescription = cargoDescription;
        this.cargoValueCaps = cargoValueCaps;
        this.route = route;
    }

    public void applyEta(Double etaHours) {
        this.etaHours = etaHours;
    }

    public void applyRisk(Integer riskScore, String riskStatus, String recommendation) {
        this.riskScore = riskScore;
        this.riskStatus = riskStatus;
        this.recommendation = recommendation;
    }

    public UUID getId() {
        return id;
    }

    public String getOrigin() {
        return origin;
    }

    public String getDestination() {
        return destination;
    }

    public LocalDate getDepartureDate() {
        return departureDate;
    }

    public String getCargoDescription() {
        return cargoDescription;
    }

    public int getCargoValueCaps() {
        return cargoValueCaps;
    }

    public Route getRoute() {
        return route;
    }

    public Double getEtaHours() {
        return etaHours;
    }

    public Integer getRiskScore() {
        return riskScore;
    }

    public String getRiskStatus() {
        return riskStatus;
    }

    public String getRecommendation() {
        return recommendation;
    }

    public String getStatus() {
        return status;
    }

    public OffsetDateTime getCreatedAt() {
        return createdAt;
    }
}
