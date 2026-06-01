package com.karavany.common.health;

import org.bson.Document;
import org.springframework.data.mongodb.core.MongoTemplate;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.time.OffsetDateTime;
import java.util.LinkedHashMap;
import java.util.Map;

/** Готовность каркаса: доступность PostgreSQL и MongoDB. */
@RestController
@RequestMapping("/api/health")
public class HealthController {

    private final JdbcTemplate jdbcTemplate;
    private final MongoTemplate mongoTemplate;

    public HealthController(JdbcTemplate jdbcTemplate, MongoTemplate mongoTemplate) {
        this.jdbcTemplate = jdbcTemplate;
        this.mongoTemplate = mongoTemplate;
    }

    @GetMapping
    public Map<String, Object> health() {
        Map<String, Object> result = new LinkedHashMap<>();
        result.put("service", "karavany");
        result.put("timestamp", OffsetDateTime.now().toString());
        result.put("postgres", checkPostgres());
        result.put("mongo", checkMongo());
        boolean up = "up".equals(result.get("postgres")) && "up".equals(result.get("mongo"));
        result.put("status", up ? "ok" : "degraded");
        return result;
    }

    private String checkPostgres() {
        try {
            jdbcTemplate.queryForObject("SELECT 1", Integer.class);
            return "up";
        } catch (Exception e) {
            return "down";
        }
    }

    private String checkMongo() {
        try {
            mongoTemplate.executeCommand(new Document("ping", 1));
            return "up";
        } catch (Exception e) {
            return "down";
        }
    }
}
