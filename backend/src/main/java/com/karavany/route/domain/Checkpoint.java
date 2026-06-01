package com.karavany.route.domain;

import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

import java.util.UUID;

@Entity
@Table(name = "checkpoint")
public class Checkpoint {

    @Id
    private UUID id;
    private String code;
    private String name;

    protected Checkpoint() {
    }

    public UUID getId() {
        return id;
    }

    public String getCode() {
        return code;
    }

    public String getName() {
        return name;
    }
}
