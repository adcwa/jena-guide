import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.concurrent.TimeUnit;
import org.apache.jena.query.QueryExecution;
import org.apache.jena.query.ResultSetFormatter;
import org.apache.jena.rdf.model.Model;
import org.apache.jena.riot.RDFDataMgr;
import org.apache.jena.shacl.Shapes;
import org.apache.jena.shacl.ShaclValidator;
import org.apache.jena.shacl.ValidationReport;

public final class Demo {
    public static void main(String[] args) throws IOException {
        Model data = RDFDataMgr.loadModel("data.ttl");
        Model shapeModel = RDFDataMgr.loadModel("shapes.ttl");
        try {
            RDFDataMgr.read(data, "ontology.ttl");
            Shapes shapes = Shapes.parse(shapeModel.getGraph());
            ValidationReport report = ShaclValidator.get()
                    .validate(shapes, data.getGraph());
            if (!report.conforms()) {
                throw new IllegalStateException(
                        "Data validation failed; stop before calculating costs.");
            }
            String sparql = Files.readString(
                    Path.of("impact.rq"), StandardCharsets.UTF_8);
            try (QueryExecution execution = QueryExecution.model(data)
                    .query(sparql).timeout(10, TimeUnit.SECONDS).build()) {
                ResultSetFormatter.out(System.out, execution.execSelect());
            }
        } finally {
            shapeModel.close();
            data.close();
        }
    }
}
