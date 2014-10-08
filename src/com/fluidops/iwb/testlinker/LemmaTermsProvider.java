package com.fluidops.iwb.testlinker;

import java.io.BufferedReader;
import java.io.File;
import java.io.InputStreamReader;
import java.io.Serializable;
import java.util.ArrayList;
import java.util.List;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import org.apache.log4j.Logger;
import org.openrdf.model.Statement;
import org.openrdf.model.URI;
import org.openrdf.model.ValueFactory;
import org.openrdf.model.impl.ValueFactoryImpl;
import org.openrdf.model.vocabulary.RDF;
import org.openrdf.model.vocabulary.RDFS;
import org.openrdf.query.BindingSet;
import org.openrdf.query.MalformedQueryException;
import org.openrdf.query.QueryEvaluationException;
import org.openrdf.query.TupleQuery;
import org.openrdf.query.TupleQueryResult;
import org.openrdf.repository.RepositoryException;

import com.fluidops.iwb.api.EndpointImpl;
import com.fluidops.iwb.api.ReadDataManager;
import com.fluidops.iwb.api.query.QueryBuilder;
import com.fluidops.iwb.model.ParameterConfigDoc;
import com.fluidops.iwb.model.Vocabulary;
import com.fluidops.iwb.provider.AbstractFlexProvider;
import com.fluidops.iwb.provider.ProviderUtils;
import com.fluidops.iwb.util.Config;
import com.fluidops.iwb.util.RDFUtil;
import com.fluidops.util.FileUtil;

/**
 * Generic provider skeleton. Can be used as a basis for implementing any type
 * of data provider.
 */
public class LemmaTermsProvider extends AbstractFlexProvider<LemmaTermsProvider.Config> {
	private static final Logger logger = Logger.getLogger(EndpointImpl.class.getName());

	File taskContentStorageFolder() {
		return new File(config.workingDir);
	}
	
	//private static final String workingDir="D:\\Development\\IWB-SCORM\\fiwb\\";
	private static final String hasLemma="http://www.semanticweb.org/k0shk/ontologies/2013/5/learning#lemma";
	private static final String lemmaTermOutput=com.fluidops.iwb.util.Config.getConfig().getWorkingDir()+"lemma_term_output.txt";

	
	
	private static final long serialVersionUID = 684345323098327777L;

	public static class Config implements Serializable {
		private static final long serialVersionUID = -6759601022040845557L;

		@ParameterConfigDoc(desc="Terms query", required=true)		
		public String termsQuery;
		
		@ParameterConfigDoc(desc="Terms dictionary", required=true)		
		public String termsDict;
		
		@ParameterConfigDoc(desc="Working directory", required=true)		
		public String workingDir;
	}

	@Override
	public Class<? extends Config> getConfigClass() {
		return Config.class;
	}

	@Override
	public void gather(final List<Statement> res) throws Exception {
		// collect tasks
		ReadDataManager dm = EndpointImpl.api().getDataManager();;
    	QueryBuilder<TupleQuery> queryBuilder = QueryBuilder.createTupleQuery(config.termsQuery).infer(false);
    	//logger.warn(tasksQuery);
    	TupleQuery query = queryBuilder.build(dm);
    	TupleQueryResult terms = query.evaluate();
    	while (terms.hasNext()) {
    		BindingSet bs = terms.next();
			ValueFactory vf = ValueFactoryImpl.getInstance();
    		URI termURI = vf.createURI(bs.getValue(terms.getBindingNames().get(0)).stringValue());
    		String termLabel = bs.getValue(terms.getBindingNames().get(1)).stringValue();

    		String[] lemmas = generateLemmas(termLabel);
    		System.out.println(termLabel + ": " + lemmas.length);
    		for(String lemma : lemmas){
    			if(!lemma.isEmpty()){
        			URI hasLemmaURI=vf.createURI(hasLemma);
        			res.add(ProviderUtils.createLiteralStatement(termURI, hasLemmaURI,
        					lemma));
    			}
    		}
    	}
	}
	

	
	private String[] generateLemmas(String term) throws Exception{
		runNLPTool(term);
		String result_content=readFile(lemmaTermOutput);
		return getAllLemmas(result_content); 
	}
		
	private String readFile(String file_name) throws Exception {
    	File file = new File(taskContentStorageFolder(), file_name);
		return FileUtil.getFileContent(file);
		//return "Плоская монохроматическая волна (<LU LEMMA=\"расстояние\" CAT=\"N\" FLX=\"NEUTER_E\" Case=\"nom\" Nb=\"sg\"><LU LEMMA=\"расстояние\" CAT=\"N\" FLX=\"NEUTER_E\" Case=\"acc\" Nb=\"sg\"><LU LEMMA=\"расстояние\" CAT=\"N\" FLX=\"NEUTER_E\" Case=\"acc\" Nb=\"pl\">расстояние</LU></LU></LU> а велико, λ = 400 нм) с интенсивностью J0 падает по нормали на круглое отверстие с диаметром равным 2,0 мм. На экране, находящемся на <LU LEMMA=\"расстояние\" CAT=\"N\" FLX=\"NEUTER_E\" Case=\"loc\" Nb=\"sg\">расстоянии</LU> b = 2 м наблюдается дифракционная картина. Амплитуде в (·)Р (центра экрана) соответствует один из <LU LEMMA=\"вектор\" CAT=\"N\" FLX=\"MASC_HARD\" Case=\"gen\" Nb=\"pl\">векторов</LU>, показанных на векторной диаграмме. Назовите номер вектора, соответствующего данному отверстию. <img src=\"http://open.ifmo.ru/images/7/79/2268861_dif32.gif\"/> Среди ответов правильного нет. 1 2 3 4 5";
	}

	
	private String[] getAllLemmas(String fileContent){
		return fileContent.split(System.getProperty("line.separator"));
//		 Matcher m = Pattern.compile("LEMMA=[\"']?((?:.(?![\"']?\\s+(?:\\S+)=|[>\"']))+.)[\"']?")
//			     .matcher(fileContent);
//			 while (m.find()) {
//				 String str = m.group();
//				 lemmas.add(str.substring(7, str.length()-1).toLowerCase());
//			 }	
//		
//		return lemmas;
	}
	
	private void runNLPTool(String term) throws Exception {
        String [] Command = null;

        //TODO: replace command
        if (System.getProperty("os.name").equals("Linux")) {
            Command = new String[8];
        	Command[0] = "python";
        	Command[1] = config.workingDir+"scripts/nlp/get_lemma.py";
            Command[2] = "-t";
            Command[3]= term;
            Command[4] = "-d"; 
            Command[5] = config.termsDict;
            Command[6] = "-f";
            Command[7] = lemmaTermOutput;

        }
        if (System.getProperty("os.name").equals("Mac OS X")) {
            Command = new String[5];
            Command[0] = "python";
            Command[1] = "./scripts/nlp/get_lemma.py";
            Command[2] = "-t \""+term+"\"";
            Command[3] = "-d " + config.termsDict;
            Command[4] = " -f "+lemmaTermOutput;
        }
        if (System.getProperty("os.name").equals("Windows 8.1")) {
            Command = new String[8];
        	Command[0] = "C:/Python27/python.exe";
        	Command[1] = config.workingDir+"scripts\\nlp\\get_lemma.py";
            Command[2] = "-t";
            Command[3]= term;
            Command[4] = "-d"; 
            Command[5] = config.termsDict;
            Command[6] = "-f";
            Command[7] = lemmaTermOutput;
        }
        if (System.getProperty("os.name").equals("Solaris")) {
            Command = new String[5];
            Command[0] = "python";
            Command[1] = "./scripts/nlp/get_lemma.py";
            Command[2] = "--t \""+term+"\"";
            Command[3] = "-d " + config.termsDict;
            Command[4] = " -f "+lemmaTermOutput;
        }
        if (Command == null) {
                System.out.print("OS not supported ");
                System.out.println(System.getProperty("os.name"));
                return;
                }
        
        Process Findspace = Runtime.getRuntime().exec(Command);
        int res = Findspace.waitFor();

//        for(String line : Command){
//            System.out.println(line);
//        }
        BufferedReader Resultset = new BufferedReader(
                        new InputStreamReader (
                        Findspace.getErrorStream()));

//        String line;
//        while ((line = Resultset.readLine()) != null) {
//                logger.warn(line);
//                System.out.println(line);
//        }
	}
	
}