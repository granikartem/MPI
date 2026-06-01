package com.karavany.risk;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.client.SimpleClientHttpRequestFactory;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestClient;

import java.util.List;
import java.util.Optional;

/** Клиент внешней системы Wasteland Intel (в dev — WireMock-заглушка). */
@Component
public class WastelandIntelClient {

    private final RestClient client;

    public WastelandIntelClient(@Value("${intel.base-url}") String baseUrl) {
        SimpleClientHttpRequestFactory rf = new SimpleClientHttpRequestFactory();
        rf.setConnectTimeout(2000);
        rf.setReadTimeout(2000);
        this.client = RestClient.builder().baseUrl(baseUrl).requestFactory(rf).build();
    }

    /** Возвращает отчёт об угрозах или пусто, если источник недоступен. */
    public Optional<ThreatReport> fetchThreats(List<String> segments) {
        try {
            ThreatReport report = client.get()
                    .uri(uri -> uri.path("/threats")
                            .queryParam("segments", String.join(",", segments))
                            .build())
                    .retrieve()
                    .body(ThreatReport.class);
            return Optional.ofNullable(report);
        } catch (Exception e) {
            return Optional.empty();
        }
    }

    public record ThreatReport(String asOf, List<SegmentThreat> segments) {
    }

    public record SegmentThreat(String segment, int threatLevel, List<String> threats) {
    }
}
