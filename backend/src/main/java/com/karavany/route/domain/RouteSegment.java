package com.karavany.route.domain;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.ManyToOne;
import jakarta.persistence.Table;

import java.util.UUID;

@Entity
@Table(name = "route_segment")
public class RouteSegment {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private UUID id;

    @ManyToOne
    @JoinColumn(name = "route_id")
    private Route route;

    private int ord;

    @ManyToOne
    @JoinColumn(name = "from_checkpoint_id")
    private Checkpoint from;

    @ManyToOne
    @JoinColumn(name = "to_checkpoint_id")
    private Checkpoint to;

    @Column(name = "distance_km")
    private double distanceKm;

    protected RouteSegment() {
    }

    public RouteSegment(Route route, int ord, Checkpoint from, Checkpoint to, double distanceKm) {
        this.route = route;
        this.ord = ord;
        this.from = from;
        this.to = to;
        this.distanceKm = distanceKm;
    }

    public int getOrd() {
        return ord;
    }

    public Checkpoint getFrom() {
        return from;
    }

    public Checkpoint getTo() {
        return to;
    }

    public double getDistanceKm() {
        return distanceKm;
    }

    public String segmentKey() {
        return from.getCode() + "-" + to.getCode();
    }
}
