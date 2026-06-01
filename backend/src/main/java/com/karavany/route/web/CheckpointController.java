package com.karavany.route.web;

import com.karavany.route.repository.CheckpointRepository;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
@RequestMapping("/api/checkpoints")
public class CheckpointController {

    private final CheckpointRepository checkpointRepository;

    public CheckpointController(CheckpointRepository checkpointRepository) {
        this.checkpointRepository = checkpointRepository;
    }

    @GetMapping
    @Transactional(readOnly = true)
    public List<CheckpointResponse> list() {
        return checkpointRepository.findAll().stream()
                .map(c -> new CheckpointResponse(c.getCode(), c.getName()))
                .toList();
    }

    public record CheckpointResponse(String code, String name) {
    }
}
