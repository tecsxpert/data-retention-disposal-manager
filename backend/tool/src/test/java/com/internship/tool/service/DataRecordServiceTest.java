package com.internship.tool.service;

import com.internship.tool.entity.DataRecord;
import com.internship.tool.entity.dto.DataRecordRequest;
import com.internship.tool.entity.dto.DataRecordResponse;
import com.internship.tool.exception.ResourceNotFoundException;
import com.internship.tool.repository.DataRecordRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageImpl;
import org.springframework.data.domain.PageRequest;
import org.springframework.web.client.RestTemplate;

import java.time.LocalDate;
import java.util.List;
import java.util.Optional;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class DataRecordServiceTest {

    @Mock
    private DataRecordRepository dataRecordRepository;

    @Mock
    private RestTemplate restTemplate;

    @InjectMocks
    private DataRecordService dataRecordService;

    private DataRecord sampleRecord;
    private DataRecordRequest sampleRequest;

    @BeforeEach
    void setUp() {
        sampleRecord = DataRecord.builder()
                .id(1L)
                .name("Customer Data 2023")
                .description("Annual customer purchase records")
                .dataType("Customer Records")
                .owner("Alice Smith")
                .department("Finance")
                .retentionYears(7)
                .createdDate(LocalDate.of(2023, 1, 1))
                .expiryDate(LocalDate.of(2030, 1, 1))
                .status("ACTIVE")
                .isDeleted(false)
                .build();

        sampleRequest = new DataRecordRequest();
        sampleRequest.setName("Customer Data 2023");
        sampleRequest.setDescription("Annual customer purchase records");
        sampleRequest.setDataType("Customer Records");
        sampleRequest.setOwner("Alice Smith");
        sampleRequest.setDepartment("Finance");
        sampleRequest.setRetentionYears(7);
        sampleRequest.setCreatedDate(LocalDate.of(2023, 1, 1));
    }

    @Test
    void getAllRecords_returnsPaginatedResults() {
        Page<DataRecord> page = new PageImpl<>(List.of(sampleRecord));
        when(dataRecordRepository.findByIsDeletedFalse(any())).thenReturn(page);

        Page<DataRecordResponse> result = dataRecordService.getAllRecords(PageRequest.of(0, 10));

        assertNotNull(result);
        assertEquals(1, result.getTotalElements());
        assertEquals("Customer Data 2023", result.getContent().get(0).getName());
    }

    @Test
    void getRecordById_existingRecord_returnsRecord() {
        when(dataRecordRepository.findByIdAndIsDeletedFalse(1L))
                .thenReturn(Optional.of(sampleRecord));

        DataRecordResponse result = dataRecordService.getRecordById(1L);

        assertNotNull(result);
        assertEquals(1L, result.getId());
        assertEquals("Customer Data 2023", result.getName());
    }

    @Test
    void getRecordById_missingRecord_throwsException() {
        when(dataRecordRepository.findByIdAndIsDeletedFalse(99L))
                .thenReturn(Optional.empty());

        assertThrows(ResourceNotFoundException.class,
                () -> dataRecordService.getRecordById(99L));
    }

    @Test
    void createRecord_validRequest_savesRecord() {
        when(dataRecordRepository.save(any(DataRecord.class))).thenReturn(sampleRecord);

        DataRecordResponse result = dataRecordService.createRecord(sampleRequest);

        assertNotNull(result);
        assertEquals("Customer Data 2023", result.getName());
        verify(dataRecordRepository, times(1)).save(any(DataRecord.class));
    }

    @Test
    void createRecord_calculatesExpiryDateCorrectly() {
        when(dataRecordRepository.save(any(DataRecord.class))).thenAnswer(inv -> {
            DataRecord r = inv.getArgument(0);
            r.setId(1L);
            return r;
        });

        DataRecordResponse result = dataRecordService.createRecord(sampleRequest);

        assertEquals(LocalDate.of(2030, 1, 1), result.getExpiryDate());
    }

    @Test
    void deleteRecord_existingRecord_softDeletes() {
        when(dataRecordRepository.findByIdAndIsDeletedFalse(1L))
                .thenReturn(Optional.of(sampleRecord));

        dataRecordService.deleteRecord(1L);

        assertTrue(sampleRecord.getIsDeleted());
        assertEquals("DISPOSED", sampleRecord.getStatus());
        verify(dataRecordRepository).save(sampleRecord);
    }

    @Test
    void deleteRecord_missingRecord_throwsException() {
        when(dataRecordRepository.findByIdAndIsDeletedFalse(99L))
                .thenReturn(Optional.empty());

        assertThrows(ResourceNotFoundException.class,
                () -> dataRecordService.deleteRecord(99L));
    }

    @Test
    void updateRecord_existingRecord_updatesFields() {
        when(dataRecordRepository.findByIdAndIsDeletedFalse(1L))
                .thenReturn(Optional.of(sampleRecord));
        when(dataRecordRepository.save(any())).thenReturn(sampleRecord);

        sampleRequest.setName("Updated Name");
        DataRecordResponse result = dataRecordService.updateRecord(1L, sampleRequest);

        verify(dataRecordRepository).save(any());
        assertNotNull(result);
    }

    @Test
    void updateRecord_missingRecord_throwsException() {
        when(dataRecordRepository.findByIdAndIsDeletedFalse(99L))
                .thenReturn(Optional.empty());

        assertThrows(ResourceNotFoundException.class,
                () -> dataRecordService.updateRecord(99L, sampleRequest));
    }

    @Test
    void searchRecords_emptyQuery_returnsAllRecords() {
        Page<DataRecord> page = new PageImpl<>(List.of(sampleRecord));
        when(dataRecordRepository.findByIsDeletedFalse(any())).thenReturn(page);

        Page<DataRecordResponse> result = dataRecordService
                .searchRecords("", PageRequest.of(0, 10));

        assertEquals(1, result.getTotalElements());
    }

    @Test
    void searchRecords_withQuery_callsSearchByQuery() {
        Page<DataRecord> page = new PageImpl<>(List.of(sampleRecord));
        when(dataRecordRepository.searchByQuery(eq("customer"), any()))
                .thenReturn(page);

        Page<DataRecordResponse> result = dataRecordService
                .searchRecords("customer", PageRequest.of(0, 10));

        assertEquals(1, result.getTotalElements());
        verify(dataRecordRepository).searchByQuery(eq("customer"), any());
    }

    @Test
    void permanentDelete_existingRecord_deletesFromDb() {
        when(dataRecordRepository.findById(1L)).thenReturn(Optional.of(sampleRecord));

        dataRecordService.permanentDelete(1L);

        verify(dataRecordRepository).delete(sampleRecord);
    }

    @Test
    void permanentDelete_missingRecord_throwsException() {
        when(dataRecordRepository.findById(99L)).thenReturn(Optional.empty());

        assertThrows(ResourceNotFoundException.class,
                () -> dataRecordService.permanentDelete(99L));
    }

    @Test
    void getStats_returnsCorrectCounts() {
        when(dataRecordRepository.countByIsDeletedFalse()).thenReturn(10L);
        when(dataRecordRepository.countByStatusAndIsDeletedFalse("ACTIVE")).thenReturn(7L);
        when(dataRecordRepository.countByStatusAndIsDeletedFalse("EXPIRING")).thenReturn(2L);
        when(dataRecordRepository.countByIsDeletedTrue()).thenReturn(1L);

        var stats = dataRecordService.getStats();

        assertEquals(10L, stats.get("total"));
        assertEquals(7L, stats.get("active"));
        assertEquals(2L, stats.get("expiring"));
        assertEquals(1L, stats.get("disposed"));
    }
}
