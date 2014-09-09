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
public class TestLinkProvider extends AbstractFlexProvider<TestLinkProvider.Config> {
	private static final Logger logger = Logger.getLogger(EndpointImpl.class.getName());

	static File taskContentStorageFolder() {
		return new File(com.fluidops.iwb.util.Config.getConfig().getWorkingDir() + "lib/extensions/testlib/testdata/tasks");
	}
	
	
	private static final String hasTerm="http://www.semanticweb.org/k0shk/ontologies/2013/5/learning#hasTerm";
	
	private static final String tasksQuery="select distinct ?task where {\r\n" + 
			"   {  ?? learningRu:hasModule ?module } \r\n" + 
			"      UNION { ?module learningRu:isModuleOf  ?? }\r\n" + 
			"   \r\n" + 
			"    { ?module learningRu:hasTest ?test } \r\n" + 
			"   UNION { ?test learningRu:isTestOf ?module }.\r\n" + 
			"   \r\n" + 
			"   {?test ifmotest:hasGroupOfTasks ?group_of_tasks}\r\n" + 
			"   UNION { ?group_of_tasks ifmotest:isGroupOfTasksOf ?test }\r\n" + 
			"   \r\n" + 
			"   {?group_of_tasks ifmotest:hasTask ?task } UNION\r\n" + 
			"   {?task ifmotest:isTaskOf ?group_of_tasks }\r\n" + 
			"}";
	
	private static final String taskContentQuery="select distinct ?content where \r\n" + 
			"{ ?? ifmotest:html_content ?content }";
	
	private static final String taskAnswersQuery="SELECT distinct ?content\r\n" + 
			"WHERE { \r\n" + 
			"{ ?? ifmotest:hasAnswer ?answer . }\r\n" + 
			"UNION { ?? ifmotest:hasCorrectAnswer  ?answer . }\r\n" + 
			"?answer ifmotest:html_content ?content\r\n" + 
			" }";
	
	private static final String termMatchQueryStart="select distinct ?x where { \r\n" + 
			"   ?x rdf:type learningRu:Term .\r\n" + 
			"   ?x rdfs:label ?y\r\n" + 
			"   FILTER (lcase(str(?y)) = \"";
	private static final String termMatchQueryEnd="\")\r\n" + 
			"}";
	private static final long serialVersionUID = 684345323098327777L;

	public static class Config implements Serializable {
		private static final long serialVersionUID = -6759601022040845557L;

		@ParameterConfigDoc(desc="The identifier of the course", required=true)		
		public URI courseIdentifier;
	}

	@Override
	public Class<? extends Config> getConfigClass() {
		return Config.class;
	}

	@Override
	public void gather(final List<Statement> res) throws Exception {
		// collect tasks
		ReadDataManager dm = EndpointImpl.api().getDataManager();;
    	QueryBuilder<TupleQuery> queryBuilder = QueryBuilder.createTupleQuery(tasksQuery)
    			.resolveValue(config.courseIdentifier).infer(false);
    	//logger.warn(tasksQuery);
    	TupleQuery query = queryBuilder.build(dm);
    	TupleQueryResult tasks = query.evaluate();
    	while (tasks.hasNext()) {
    		BindingSet bs = tasks.next();
			ValueFactory vf = ValueFactoryImpl.getInstance();
    		URI taskURI = vf.createURI(bs.getValue(tasks.getBindingNames().get(0)).stringValue());
			//logger.warn("URI: "+taskURI);
    		String result_content = getTaskContent(taskURI);
    		result_content = result_content+" "+ getAnswersContent(taskURI);

    		for(String lemma : collectLemmas(taskURI,result_content)){
        		URI term=getTermByLemma(lemma);
        		if(term!=null){
        			URI hasTermURI=vf.createURI(hasTerm);
        			res.add(ProviderUtils.createStatement(taskURI, hasTermURI,
    					term));
        		}
    		}
    	}
		
				res.add(ProviderUtils.createStatement(config.courseIdentifier, RDFS.COMMENT,
						RDFUtil.literal("My demo object")));

	}
	
	private String getTaskContent(URI task) throws Exception{
		String result="";
		ReadDataManager dm = EndpointImpl.api().getDataManager();;
    	QueryBuilder<TupleQuery> queryBuilder = QueryBuilder.createTupleQuery(taskContentQuery)
    			.resolveValue(task).infer(false);

    	TupleQuery query = queryBuilder.build(dm);
    	TupleQueryResult contents = query.evaluate();
    	while (contents.hasNext()) {
    		BindingSet bs = contents.next();
    		result = result+ " "+ bs.getValue(contents.getBindingNames().get(0)).stringValue();
    	}
    	return result;
	}
	
	private String getAnswersContent(URI task) throws Exception{
		String result="";
		ReadDataManager dm = EndpointImpl.api().getDataManager();;
    	QueryBuilder<TupleQuery> queryBuilder = QueryBuilder.createTupleQuery(taskAnswersQuery)
    			.resolveValue(task).infer(false);

    	TupleQuery query = queryBuilder.build(dm);
    	TupleQueryResult contents = query.evaluate();
    	while (contents.hasNext()) {
    		BindingSet bs = contents.next();
    		result = result + " "+ bs.getValue(contents.getBindingNames().get(0)).stringValue();
    	}
    	return result;
	}
	
	private ArrayList<String> collectLemmas(URI objectURI, String content) throws Exception{
		String uri = objectURI.toString(); 
	    int index=uri.lastIndexOf('/');
		writeFile(uri.substring(index, uri.length())+".txt",content);
		runNLPTool();
		String result_content=readFile(uri.substring(index, uri.length())+".not.xml.txt");
		return getAllLemmas(result_content); 
	}
	
	private void writeFile(String file_name, String file_content) throws Exception{
    	File file = new File(taskContentStorageFolder(), file_name);
		FileUtil.writeContentToFile(file_content, file.getAbsolutePath());
	}
	
	private String readFile(String file_name) throws Exception {
    	File file = new File(taskContentStorageFolder(), file_name);
		return FileUtil.getFileContent(file);
		//return "Плоская монохроматическая волна (<LU LEMMA=\"расстояние\" CAT=\"N\" FLX=\"NEUTER_E\" Case=\"nom\" Nb=\"sg\"><LU LEMMA=\"расстояние\" CAT=\"N\" FLX=\"NEUTER_E\" Case=\"acc\" Nb=\"sg\"><LU LEMMA=\"расстояние\" CAT=\"N\" FLX=\"NEUTER_E\" Case=\"acc\" Nb=\"pl\">расстояние</LU></LU></LU> а велико, λ = 400 нм) с интенсивностью J0 падает по нормали на круглое отверстие с диаметром равным 2,0 мм. На экране, находящемся на <LU LEMMA=\"расстояние\" CAT=\"N\" FLX=\"NEUTER_E\" Case=\"loc\" Nb=\"sg\">расстоянии</LU> b = 2 м наблюдается дифракционная картина. Амплитуде в (·)Р (центра экрана) соответствует один из <LU LEMMA=\"вектор\" CAT=\"N\" FLX=\"MASC_HARD\" Case=\"gen\" Nb=\"pl\">векторов</LU>, показанных на векторной диаграмме. Назовите номер вектора, соответствующего данному отверстию. <img src=\"http://open.ifmo.ru/images/7/79/2268861_dif32.gif\"/> Среди ответов правильного нет. 1 2 3 4 5";
	}

	
	private ArrayList<String> getAllLemmas(String fileContent){
		ArrayList<String> lemmas = new ArrayList<String>();
		 Matcher m = Pattern.compile("LEMMA=[\"']?((?:.(?![\"']?\\s+(?:\\S+)=|[>\"']))+.)[\"']?")
			     .matcher(fileContent);
			 while (m.find()) {
				 String str = m.group();
				 lemmas.add(str.substring(7, str.length()-1).toLowerCase());
			 }	
		
		return lemmas;
	}
		
	private URI getTermByLemma(String lemma) throws Exception {
		String lemmaQuery=termMatchQueryStart+lemma+termMatchQueryEnd;
		ReadDataManager dm = EndpointImpl.api().getDataManager();;
    	QueryBuilder<TupleQuery> queryBuilder = QueryBuilder.createTupleQuery(lemmaQuery).infer(false);

    	TupleQuery query = queryBuilder.build(dm);
    	TupleQueryResult terms = query.evaluate();
    	//logger.warn(lemma);
    	//logger.warn(lemmaQuery);
    	if (terms.hasNext()) {
    		BindingSet bs = terms.next();
			ValueFactory vf = ValueFactoryImpl.getInstance();
    		return vf.createURI(bs.getValue(terms.getBindingNames().get(0)).stringValue());
    	}
    	return null;
	}
	
	private void runNLPTool() throws Exception {
        String [] Command = null;
        //TODO: replace command
        if (System.getProperty("os.name").equals("Linux")) {
                Command = new String[1];
                Command[0] = "df";
                }
        if (System.getProperty("os.name").equals("Mac OS X")) {
                Command = new String[1];
                Command[0] = "df";
                }
        if (System.getProperty("os.name").equals("Solaris")) {
                Command = new String[2];
                Command[0] = "df";
                Command[1] = "-k";
                }
        if (Command == null) {
                System.out.print("OS not supported ");
                System.out.println(System.getProperty("os.name"));
                return;
                }

        Process Findspace = Runtime.getRuntime().exec(Command);

        BufferedReader Resultset = new BufferedReader(
                        new InputStreamReader (
                        Findspace.getInputStream()));

        String line;
        while ((line = Resultset.readLine()) != null) {
                logger.warn(line);
                
        }
	}
	
}