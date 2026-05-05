package com.internship.tool.config;

import com.internship.tool.entity.DataRecord;
import com.internship.tool.entity.User;
import com.internship.tool.repository.DataRecordRepository;
import com.internship.tool.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.boot.CommandLineRunner;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Component;

import java.time.LocalDate;
import java.util.List;

@Component
@RequiredArgsConstructor
@Slf4j
public class DataSeeder implements CommandLineRunner {

    private final DataRecordRepository dataRecordRepository;
    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;

    @Override
    public void run(String... args) {
        seedUsers();
        seedDataRecords();
    }

    private void seedUsers() {
        if (userRepository.count() == 0) {
            userRepository.saveAll(List.of(
                User.builder().username("admin").email("admin@company.com")
                    .password(passwordEncoder.encode("admin123")).role("ADMIN").build(),
                User.builder().username("user1").email("user1@company.com")
                    .password(passwordEncoder.encode("user123")).role("USER").build()
            ));
            log.info("Seeded 2 users");
        }
    }

    private void seedDataRecords() {
        if (dataRecordRepository.count() == 0) {
            List<DataRecord> records = List.of(
                buildRecord("Customer Purchase History 2020", "Customer Records",
                    "Finance Team", "Finance", 7,
                    LocalDate.of(2020, 3, 1), "ACTIVE"),
                buildRecord("Employee Performance Reviews Q4 2022", "HR Records",
                    "HR Department", "Human Resources", 5,
                    LocalDate.of(2022, 12, 1), "ACTIVE"),
                buildRecord("Tax Filing Documents 2019", "Financial Records",
                    "Accounts Team", "Finance", 10,
                    LocalDate.of(2019, 4, 15), "EXPIRING"),
                buildRecord("Marketing Campaign Data 2021", "Marketing Data",
                    "Marketing Dept", "Marketing", 3,
                    LocalDate.of(2021, 6, 1), "EXPIRING"),
                buildRecord("Product Inventory Logs Q1 2023", "Operational Data",
                    "Operations", "Operations", 5,
                    LocalDate.of(2023, 1, 1), "ACTIVE"),
                buildRecord("Customer Support Tickets 2022", "Support Records",
                    "Support Team", "Customer Support", 3,
                    LocalDate.of(2022, 1, 1), "EXPIRING"),
                buildRecord("Annual Audit Report 2018", "Compliance Records",
                    "Legal Team", "Legal", 10,
                    LocalDate.of(2018, 12, 31), "ACTIVE"),
                buildRecord("Employee Onboarding Files 2023", "HR Records",
                    "HR Department", "Human Resources", 7,
                    LocalDate.of(2023, 3, 15), "ACTIVE"),
                buildRecord("Sales Pipeline Data Q2 2022", "Sales Records",
                    "Sales Team", "Sales", 5,
                    LocalDate.of(2022, 6, 30), "ACTIVE"),
                buildRecord("IT Infrastructure Logs 2021", "Technical Logs",
                    "IT Department", "IT", 3,
                    LocalDate.of(2021, 1, 1), "DISPOSED"),
                buildRecord("Vendor Contracts 2020", "Legal Documents",
                    "Procurement", "Finance", 10,
                    LocalDate.of(2020, 8, 1), "ACTIVE"),
                buildRecord("Quarterly Financial Statements Q3 2023", "Financial Records",
                    "Finance Team", "Finance", 7,
                    LocalDate.of(2023, 9, 30), "ACTIVE"),
                buildRecord("Customer Feedback Survey 2022", "Customer Data",
                    "Product Team", "Product", 3,
                    LocalDate.of(2022, 11, 1), "EXPIRING"),
                buildRecord("GDPR Consent Records 2021", "Compliance Records",
                    "Legal Team", "Legal", 5,
                    LocalDate.of(2021, 5, 25), "ACTIVE"),
                buildRecord("Software License Records 2020", "IT Records",
                    "IT Department", "IT", 5,
                    LocalDate.of(2020, 1, 1), "DISPOSED"),
                buildRecord("Training Completion Records 2023", "HR Records",
                    "HR Department", "Human Resources", 3,
                    LocalDate.of(2023, 6, 1), "ACTIVE"),
                buildRecord("Supplier Payment History 2021", "Financial Records",
                    "Accounts Team", "Finance", 7,
                    LocalDate.of(2021, 12, 1), "ACTIVE"),
                buildRecord("Customer Churn Analysis 2022", "Analytics Data",
                    "Data Team", "Analytics", 3,
                    LocalDate.of(2022, 7, 15), "EXPIRING"),
                buildRecord("Building Access Logs 2022", "Security Records",
                    "Facilities", "Operations", 2,
                    LocalDate.of(2022, 1, 1), "DISPOSED"),
                buildRecord("Product Returns Data Q4 2023", "Operational Data",
                    "Operations", "Operations", 5,
                    LocalDate.of(2023, 12, 1), "ACTIVE"),
                buildRecord("Annual Board Meeting Minutes 2019", "Corporate Records",
                    "Executive Team", "Legal", 10,
                    LocalDate.of(2019, 11, 15), "ACTIVE"),
                buildRecord("Email Archive 2020", "Communication Records",
                    "IT Department", "IT", 3,
                    LocalDate.of(2020, 12, 31), "DISPOSED"),
                buildRecord("Payroll Records 2021", "HR Records",
                    "HR Department", "Human Resources", 7,
                    LocalDate.of(2021, 12, 31), "ACTIVE"),
                buildRecord("Website Analytics 2022", "Digital Data",
                    "Marketing Dept", "Marketing", 2,
                    LocalDate.of(2022, 12, 31), "DISPOSED"),
                buildRecord("Insurance Claims Archive 2020", "Legal Documents",
                    "Legal Team", "Legal", 10,
                    LocalDate.of(2020, 6, 1), "ACTIVE"),
                buildRecord("Product Design Specifications 2023", "Technical Records",
                    "Engineering Team", "Engineering", 5,
                    LocalDate.of(2023, 2, 1), "ACTIVE"),
                buildRecord("Customer Loyalty Program Data 2022", "Customer Data",
                    "Marketing Dept", "Marketing", 5,
                    LocalDate.of(2022, 1, 1), "EXPIRING"),
                buildRecord("Cybersecurity Incident Reports 2021", "Security Records",
                    "IT Security", "IT", 7,
                    LocalDate.of(2021, 9, 1), "ACTIVE"),
                buildRecord("Research & Development Notes 2023", "R&D Data",
                    "Research Team", "Engineering", 10,
                    LocalDate.of(2023, 4, 1), "ACTIVE"),
                buildRecord("Monthly Server Performance Reports 2022", "Technical Logs",
                    "IT Department", "IT", 2,
                    LocalDate.of(2022, 12, 1), "DISPOSED")
            );

            dataRecordRepository.saveAll(records);
            log.info("Seeded 30 data records");
        }
    }

    private DataRecord buildRecord(String name, String dataType, String owner,
                                    String department, int retentionYears,
                                    LocalDate createdDate, String status) {
        return DataRecord.builder()
                .name(name)
                .dataType(dataType)
                .owner(owner)
                .department(department)
                .retentionYears(retentionYears)
                .createdDate(createdDate)
                .expiryDate(createdDate.plusYears(retentionYears))
                .status(status)
                .isDeleted("DISPOSED".equals(status))
                .build();
    }
}
