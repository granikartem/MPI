package com.karavany.risk;

import org.springframework.data.mongodb.repository.MongoRepository;

import java.util.Optional;
import java.util.UUID;

public interface RiskAssessmentRepository extends MongoRepository<RiskAssessment, String> {

    Optional<RiskAssessment> findFirstByRequestIdOrderByComputedAtDesc(UUID requestId);

    void deleteByRequestId(UUID requestId);
}
