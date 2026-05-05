package com.internship.tool.controller;

import com.internship.tool.entity.dto.DataRecordRequest;
import com.internship.tool.entity.dto.DataRecordResponse;
import com.internship.tool.service.DataRecordService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.security.SecurityRequirement;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.data.domain.Sort;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/records")
@RequiredArgsConstructor
@Tag(name = "Data Records", description = "Manage data retention records")
@SecurityRequirement(name = "bearerAuth")
@CrossOrigin(origins = "*")
public class DataRecordController {

    private final DataRecordService dataRecordService;

    @GetMapping
    @Operation(summary = "Get all records (paginated)")
    public ResponseEntity<Page<DataRecordResponse>> getAllRecords(
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "10") int size,
            @RequestParam(defaultValue = "createdAt") String sortBy,
            @RequestParam(defaultValue = "desc") String direction) {

        Sort sort = direction.equalsIgnoreCase("asc")
                ? Sort.by(sortBy).ascending()
                : Sort.by(sortBy).descending();

        Pageable pageable = PageRequest.of(page, size, sort);
        return ResponseEntity.ok(dataRecordService.getAllRecords(pageable));
    }

    @GetMapping("/{id}")
    @Operation(summary = "Get a record by ID")
    public ResponseEntity<DataRecordResponse> getRecordById(@PathVariable Long id) {
        return ResponseEntity.ok(dataRecordService.getRecordById(id));
    }

    @PostMapping
    @Operation(summary = "Create a new data record")
    @ResponseStatus(HttpStatus.CREATED)
    public ResponseEntity<DataRecordResponse> createRecord(
            @Valid @RequestBody DataRecordRequest request) {
        DataRecordResponse response = dataRecordService.createRecord(request);
        return ResponseEntity.status(HttpStatus.CREATED).body(response);
    }

    @PutMapping("/{id}")
    @Operation(summary = "Update an existing record")
    public ResponseEntity<DataRecordResponse> updateRecord(
            @PathVariable Long id,
            @Valid @RequestBody DataRecordRequest request) {
        return ResponseEntity.ok(dataRecordService.updateRecord(id, request));
    }

    
    @DeleteMapping("/{id}")
    @PreAuthorize("hasAnyRole('ADMIN', 'USER')")
    public ResponseEntity<Map<String, String>> deleteRecord(@PathVariable Long id) {
       dataRecordService.deleteRecord(id);
       return ResponseEntity.ok(Map.of("message", "Record successfully disposed"));
    }

    // Add an admin-only endpoint for hard management
    @DeleteMapping("/{id}/permanent")
    @PreAuthorize("hasRole('ADMIN')")
    @Operation(summary = "Permanently delete a record (admin only)")
       public ResponseEntity<Map<String, String>> permanentDelete(@PathVariable Long id) {
       dataRecordService.permanentDelete(id);
       return ResponseEntity.ok(Map.of("message", "Record permanently removed"));
    }

    @PostMapping("/{id}/analyze")
    @Operation(summary = "Analyze a record with AI and store the result")
    public ResponseEntity<DataRecordResponse> analyzeRecord(@PathVariable Long id) {
        return ResponseEntity.ok(dataRecordService.analyzeRecord(id));
    }

    @GetMapping("/search")
    @Operation(summary = "Search records by keyword")
    public ResponseEntity<Page<DataRecordResponse>> searchRecords(
            @RequestParam(required = false) String q,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "10") int size) {

        Pageable pageable = PageRequest.of(page, size, Sort.by("createdAt").descending());
        return ResponseEntity.ok(dataRecordService.searchRecords(q, pageable));
    }

    @GetMapping("/stats")
    @Operation(summary = "Get dashboard statistics")
    public ResponseEntity<Map<String, Long>> getStats() {
        return ResponseEntity.ok(dataRecordService.getStats());
    }

    @GetMapping("/export")
    @Operation(summary = "Export all records as CSV")
    public ResponseEntity<byte[]> exportCsv() {
        StringBuilder csv = new StringBuilder();
        csv.append("ID,Name,DataType,Owner,Department,Status,RetentionYears,CreatedDate,ExpiryDate\n");

        dataRecordService.getAllRecords(PageRequest.of(0, Integer.MAX_VALUE))
                .getContent()
                .forEach(r -> csv.append(String.format("%d,%s,%s,%s,%s,%s,%d,%s,%s\n",
                        r.getId(),
                        escapeCsv(r.getName()),
                        escapeCsv(r.getDataType()),
                        escapeCsv(r.getOwner()),
                        escapeCsv(r.getDepartment()),
                        r.getStatus(),
                        r.getRetentionYears(),
                        r.getCreatedDate(),
                        r.getExpiryDate()
                )));

        byte[] csvBytes = csv.toString().getBytes();
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.parseMediaType("text/csv"));
        headers.setContentDispositionFormData("attachment", "data-records.csv");

        return ResponseEntity.ok().headers(headers).body(csvBytes);
    }

    private String escapeCsv(String value) {
        if (value == null) return "";
        if (value.contains(",") || value.contains("\"")) {
            return "\"" + value.replace("\"", "\"\"") + "\"";
        }
        return value;
    }
}