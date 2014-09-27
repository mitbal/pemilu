import weka.core.Instances;
import weka.core.converters.ArffSaver;
import weka.core.converters.CSVLoader;

import java.io.File;

public class CVS2Arff {
	
	public static void main(String[] args) throws Exception {
		if(args.length != 2) {
			System.out.println("\nUsage: CVS2Arff <input.csv> <output.arff>\n");
			System.exit(1);
		}

		// Load CSV
		CSVLoader loader = new CSVLoader();
		loader.setSource(new File(args[0]));
		Instances data = loader.getDataSet();

		// Save ARFF
		ArffSaver saver = new ArffSaver();
		saver.setInstances(data);
		saver.setFile(new File(args[1]));
		saver.writeBatch();
	}
}