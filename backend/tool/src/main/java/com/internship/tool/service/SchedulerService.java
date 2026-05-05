package com.internship.tool.service;

import com.internship.tool.entity.DataRecord;
import com.internship.tool.repository.DataRecordRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDate;
import java.util.List;

@Service
@RequiredArgsConstructor
@Slf4j
public class SchedulerService {

    private final DataRecordRepository dataRecordRepository;
    private final EmailService emailService;

    @Value("${spring.mail.username}")
    private String adminEmail;

    @Scheduled(cron = "0 0 8 * * *")
    @Transactional
    public void sendDailyExpiryReminder() {
        log.info("Running daily expiry check scheduler...");

        LocalDate thirtyDaysFromNow = LocalDate.now().plusDays(30);

        List<DataRecord> expiringRecords = dataRecordRepository
                .findByExpiryDateBeforeAndIsDeletedFalseAndStatus(
                        thirtyDaysFromNow, "ACTIVE");

        if (!expiringRecords.isEmpty()) {
            log.info("Found {} records expiring within 30 days", expiringRecords.size());
            emailService.sendExpiryReminder(adminEmail, expiringRecords);

            // Mark them as EXPIRING status
            expiringRecords.forEach(record -> {
                record.setStatus("EXPIRING");
                dataRecordRepository.save(record);
            });
        } else {
            log.info("No records expiring in the next 30 days");
        }
    }
}
