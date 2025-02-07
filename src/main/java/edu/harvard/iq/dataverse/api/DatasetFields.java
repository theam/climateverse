package edu.harvard.iq.dataverse.api;

import edu.harvard.iq.dataverse.DatasetFieldServiceBean;
import edu.harvard.iq.dataverse.DatasetFieldType;
import jakarta.ejb.EJB;
import jakarta.ws.rs.GET;
import jakarta.ws.rs.Path;
import jakarta.ws.rs.Produces;
import jakarta.ws.rs.core.Response;
import software.amazon.awssdk.auth.credentials.AwsBasicCredentials;
import software.amazon.awssdk.auth.credentials.StaticCredentialsProvider;
import software.amazon.awssdk.regions.Region;
import software.amazon.awssdk.services.s3.S3Client;
import software.amazon.awssdk.services.s3.model.GetObjectRequest;
import software.amazon.awssdk.services.s3.model.GetObjectResponse;
import software.amazon.awssdk.services.s3.model.ListObjectsV2Request;
import software.amazon.awssdk.services.s3.model.ListObjectsV2Response;
import software.amazon.awssdk.services.s3.presigner.S3Presigner;
import software.amazon.awssdk.services.s3.presigner.model.GetObjectPresignRequest;

import java.time.Duration;
import java.util.List;
import java.util.stream.Collectors;

import static edu.harvard.iq.dataverse.util.json.JsonPrinter.jsonDatasetFieldTypes;

/**
 * Api bean for managing dataset fields.
 */
@Path("datasetfields")
@Produces("application/json")
public class DatasetFields extends AbstractApiBean {

    @EJB
    DatasetFieldServiceBean datasetFieldService;

    private static final String BUCKET_NAME = "climateverse";
    private static final Region REGION = Region.US_EAST_1; // Change to your region

    @GET
    @Path("facetables")
    public Response listAllFacetableDatasetFields() {
        List<DatasetFieldType> datasetFieldTypes = datasetFieldService.findAllFacetableFieldTypes();
        return ok(jsonDatasetFieldTypes(datasetFieldTypes));
    }

    @GET
    @Path("scorecards")
    public Response listScorecardImages() {
        String awsAccessId = System.getProperty("dataverse.s3.aws.access.id");
        String awsAccessKey = System.getProperty("dataverse.s3.aws.access.key");
        AwsBasicCredentials awsCreds = AwsBasicCredentials.create(awsAccessId, awsAccessKey);

        S3Client s3 = S3Client.builder()
                .region(REGION)
                .credentialsProvider(StaticCredentialsProvider.create(awsCreds))
                .build();

        S3Presigner presigner = S3Presigner.builder()
                .region(REGION)
                .credentialsProvider(StaticCredentialsProvider.create(awsCreds))
                .build();

        ListObjectsV2Request listObjectsReqManual = ListObjectsV2Request.builder()
                .bucket(BUCKET_NAME)
                .build();

        ListObjectsV2Response listObjResponse = s3.listObjectsV2(listObjectsReqManual);

        List<String> imageUrls = listObjResponse.contents().stream()
                .filter(s3Object -> {
                    GetObjectRequest getObjectRequest = GetObjectRequest.builder()
                            .bucket(BUCKET_NAME)
                            .key(s3Object.key())
                            .build();

                    GetObjectResponse getObjectResponse = s3.getObject(getObjectRequest).response();
                    return "included".equals(getObjectResponse.metadata().get("freq"));
                })
                .map(s3Object -> {
                    GetObjectRequest getObjectRequest = GetObjectRequest.builder()
                            .bucket(BUCKET_NAME)
                            .key(s3Object.key())
                            .build();

                    GetObjectPresignRequest presignRequest = GetObjectPresignRequest.builder()
                            .getObjectRequest(getObjectRequest)
                            .signatureDuration(Duration.ofMinutes(10))
                            .build();

                    return presigner.presignGetObject(presignRequest).url().toString();
                })
                .collect(Collectors.toList());

        return Response.ok(imageUrls).build();
    }
}
