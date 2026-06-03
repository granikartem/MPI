package com.karavany.organization.service;

import com.karavany.audit.AuditEvent;
import com.karavany.audit.AuditEventRepository;
import com.karavany.organization.domain.AppUser;
import com.karavany.organization.domain.Organization;
import com.karavany.organization.repository.AppUserRepository;
import com.karavany.organization.repository.OrganizationRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.HexFormat;
import java.util.List;
import java.util.Locale;
import java.util.UUID;

@Service
public class OrganizationService {

    private static final List<String> TIERS = List.of("BASIC", "STANDARD", "PRO");

    private final OrganizationRepository organizationRepository;
    private final AppUserRepository userRepository;
    private final AuditEventRepository auditEventRepository;

    public OrganizationService(OrganizationRepository organizationRepository,
                               AppUserRepository userRepository,
                               AuditEventRepository auditEventRepository) {
        this.organizationRepository = organizationRepository;
        this.userRepository = userRepository;
        this.auditEventRepository = auditEventRepository;
    }

    public record CreateOrganizationCommand(String name, String subscriptionTier,
                                            String legalAddress, String primaryContact,
                                            String contactChannel, String region,
                                            FirstDispatcherCommand firstDispatcher) {
    }

    public record FirstDispatcherCommand(String fullName, String login,
                                         String initialPassword, String contactChannel) {
    }

    public record OrganizationProvisioning(Organization organization,
                                           AppUser firstDispatcher,
                                           int userCount) {
    }

    @Transactional(readOnly = true)
    public List<OrganizationProvisioning> findAll() {
        return organizationRepository.findAllByOrderByCreatedAtDesc().stream()
                .map(o -> new OrganizationProvisioning(o, null, userRepository.countByOrganization_Id(o.getId())))
                .toList();
    }

    @Transactional
    public OrganizationProvisioning create(CreateOrganizationCommand command) {
        String name = required(command.name(), "Название организации обязательно");
        String tier = normalizeTier(command.subscriptionTier());
        if (organizationRepository.findByNameIgnoreCase(name).isPresent()) {
            throw new IllegalArgumentException("Организация с таким названием уже существует");
        }

        FirstDispatcherCommand dispatcherCommand = command.firstDispatcher();
        if (dispatcherCommand != null) {
            validateDispatcher(dispatcherCommand);
        }

        Organization organization = organizationRepository.save(new Organization(
                generateTenantKey(), name, tier,
                clean(command.legalAddress()), clean(command.primaryContact()),
                clean(command.contactChannel()), clean(command.region())
        ));

        AppUser dispatcher = null;
        if (dispatcherCommand != null) {
            dispatcher = userRepository.save(new AppUser(
                    organization,
                    required(dispatcherCommand.fullName(), "ФИО первого диспетчера обязательно"),
                    required(dispatcherCommand.login(), "Логин первого диспетчера обязателен"),
                    passwordHash(required(dispatcherCommand.initialPassword(), "Начальный пароль обязателен")),
                    "DISPATCHER",
                    clean(dispatcherCommand.contactChannel())
            ));
        }

        auditEventRepository.save(AuditEvent.organizationCreated(
                organization.getId(),
                dispatcher == null ? null : dispatcher.getId(),
                organization.getName(),
                organization.getSubscriptionTier(),
                dispatcher == null ? null : dispatcher.getLogin()
        ));

        return new OrganizationProvisioning(organization, dispatcher, dispatcher == null ? 0 : 1);
    }

    private void validateDispatcher(FirstDispatcherCommand dispatcher) {
        String login = required(dispatcher.login(), "Логин первого диспетчера обязателен");
        required(dispatcher.fullName(), "ФИО первого диспетчера обязательно");
        required(dispatcher.initialPassword(), "Начальный пароль обязателен");
        if (userRepository.findByLoginIgnoreCase(login).isPresent()) {
            throw new IllegalArgumentException("Пользователь с таким логином уже существует");
        }
    }

    private String normalizeTier(String value) {
        String tier = required(value, "Уровень подписки обязателен").toUpperCase(Locale.ROOT);
        if (!TIERS.contains(tier)) {
            throw new IllegalArgumentException("Неизвестный уровень подписки: " + value);
        }
        return tier;
    }

    private String generateTenantKey() {
        return "tnt_" + UUID.randomUUID().toString().substring(0, 8);
    }

    private String passwordHash(String initialPassword) {
        try {
            MessageDigest digest = MessageDigest.getInstance("SHA-256");
            byte[] hash = digest.digest(("karavany:" + initialPassword).getBytes(StandardCharsets.UTF_8));
            return "sha256:" + HexFormat.of().formatHex(hash);
        } catch (NoSuchAlgorithmException e) {
            throw new IllegalStateException("SHA-256 is not available", e);
        }
    }

    private String required(String value, String message) {
        String cleaned = clean(value);
        if (cleaned == null) {
            throw new IllegalArgumentException(message);
        }
        return cleaned;
    }

    private String clean(String value) {
        if (value == null || value.isBlank()) {
            return null;
        }
        return value.trim();
    }
}
