package com.karavany.route.domain;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.OneToMany;
import jakarta.persistence.OrderBy;
import jakarta.persistence.Table;

import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

@Entity
@Table(name = "route")
public class Route {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private UUID id;

    private String name;

    @Column(name = "is_template")
    private boolean template;

    @OneToMany(mappedBy = "route")
    @OrderBy("ord ASC")
    private List<RouteSegment> segments = new ArrayList<>();

    protected Route() {
    }

    public Route(String name, boolean template) {
        this.name = name;
        this.template = template;
    }

    public UUID getId() {
        return id;
    }

    public String getName() {
        return name;
    }

    public boolean isTemplate() {
        return template;
    }

    public List<RouteSegment> getSegments() {
        return segments;
    }
}
