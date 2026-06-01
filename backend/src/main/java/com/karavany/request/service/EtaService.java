package com.karavany.request.service;

import com.karavany.route.domain.Route;
import com.karavany.route.domain.RouteSegment;
import org.springframework.stereotype.Service;

/** UC-1, FR-5: расчёт ETA по длине маршрута и средней скорости каравана. */
@Service
public class EtaService {

    /** Средняя скорость гужевого каравана, км/ч. */
    private static final double CARAVAN_SPEED_KMH = 4.0;

    public double computeHours(Route route) {
        double totalKm = route.getSegments().stream()
                .mapToDouble(RouteSegment::getDistanceKm)
                .sum();
        return totalKm / CARAVAN_SPEED_KMH;
    }
}
