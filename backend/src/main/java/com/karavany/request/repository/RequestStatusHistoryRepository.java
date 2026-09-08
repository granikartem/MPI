package com.karavany.request.repository;

import com.karavany.request.domain.RequestStatusHistory;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Collection;
import java.util.List;
import java.util.UUID;

public interface RequestStatusHistoryRepository extends JpaRepository<RequestStatusHistory, UUID> {

    List<RequestStatusHistory> findByRequest_IdOrderByOccurredAtAsc(UUID requestId);

    List<RequestStatusHistory> findByRequest_IdInOrderByOccurredAtAsc(Collection<UUID> requestIds);
}
