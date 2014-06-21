package com.fluidops.iwb.demo;

import static com.google.common.collect.Iterables.filter;
import static com.google.common.collect.Iterables.isEmpty;
import static java.lang.String.format;

import java.io.File;
import java.io.FilenameFilter;
import java.io.IOException;
import java.rmi.RemoteException;
import java.util.ArrayList;
import java.util.Date;
import java.util.List;
import java.util.Set;

import org.apache.commons.io.FileUtils;
import org.apache.log4j.Logger;
import org.openrdf.model.URI;
import org.openrdf.model.ValueFactory;
import org.openrdf.model.impl.ValueFactoryImpl;
import org.openrdf.query.BindingSet;
import org.openrdf.query.MalformedQueryException;
import org.openrdf.query.QueryEvaluationException;
import org.openrdf.query.TupleQuery;
import org.openrdf.query.TupleQueryResult;
import org.openrdf.repository.RepositoryException;

import com.fluidops.ajax.components.FContainer;
import com.fluidops.iwb.api.EndpointImpl;
import com.fluidops.iwb.api.Context.ContextLabel;
import com.fluidops.iwb.api.Context.ContextType;
import com.fluidops.iwb.api.ReadDataManager;
import com.fluidops.iwb.api.WikiStorageBulkServiceImpl.WikiPageMeta;
import com.fluidops.iwb.api.query.QueryBuilder;
import com.fluidops.iwb.api.solution.SolutionService;
import com.fluidops.iwb.model.Vocabulary;
import com.fluidops.iwb.page.PageContext;
import com.fluidops.iwb.ui.editor.SemWikiUtil;
import com.fluidops.iwb.util.Config;
import com.fluidops.iwb.util.DateTimeUtil;
import com.fluidops.iwb.util.IWBFileUtil;
import com.fluidops.iwb.wiki.FluidWikiModel;
import com.fluidops.iwb.wiki.WikiBot;
import com.fluidops.iwb.wiki.WikiStorage;
import com.fluidops.iwb.wiki.WikiStorage.WikiRevision;
import com.fluidops.iwb.wiki.Wikimedia;
import com.fluidops.util.FileUtil;
import com.fluidops.util.GenUtil;
import com.fluidops.util.StringUtil;
import com.fluidops.util.ZipUtil;
import com.google.common.base.Predicate;
import com.google.common.base.Throwables;
import com.google.common.collect.Lists;

/**
 * API for access to wiki storage providing various convenience functions.
 * 
 * @author as
 */
public class SCORMExportService {
	
	private static final Logger logger = Logger.getLogger(EndpointImpl.class.getName());
    public static final String SCORM_DRIVER_DIRNAME = "lib/extensions" + "/SCORMDriver/";
	public static final String HTML_CONTENT_DESTINATION = "scormcontent";

    public static final String WIKIEXPORT_STORAGE = IWBFileUtil.DATA_DIRECTORY + "/solutions/";
    public static final String WIKIBOOTSTRAP_REL_PATH = IWBFileUtil.DATA_DIRECTORY;

	public static File getWikiExportStorageFolder() {
		logger.warn(Config.getConfig().getWorkingDir() + WIKIEXPORT_STORAGE);
		return new File(Config.getConfig().getWorkingDir() + WIKIEXPORT_STORAGE);
	}

	public static File getSCORMStorageFolder() {
		logger.warn(Config.getConfig().getWorkingDir() + SCORM_DRIVER_DIRNAME);
		return new File(Config.getConfig().getWorkingDir() + SCORM_DRIVER_DIRNAME);
	}

	
    private final WikiStorage ws;

    public SCORMExportService(WikiStorage wikiStorage)
    {
        this.ws = wikiStorage;
    }

	static File wikiStorageRelFolder(File baseDir) {
		return new File(baseDir, HTML_CONTENT_DESTINATION);
	}
	
    public static String createWikiBootstrap(URI pageURI, String mainTemplateName,
    		String finalTemplateName, String lectureTemplateName, String lectureQuery,
    		FContainer parent, PageContext pc) 
    				throws IOException, QueryEvaluationException, MalformedQueryException, RepositoryException
    {


        File storagePath = getWikiExportStorageFolder();
        if (!storagePath.exists())
        	GenUtil.mkdirs(storagePath);        
        
        File tempDir = GenUtil.createTmpDir("SCORMCourse");
        
        File wikiBootstrapFolder = wikiStorageRelFolder(tempDir);
       	GenUtil.mkdirs(wikiBootstrapFolder);
        
        try 
        {
        	GenUtil.copyFolder(getSCORMStorageFolder(), tempDir);
        	
        	createWebPage(wikiBootstrapFolder, "index.html", mainTemplateName, pageURI , parent, pc, false, null);
        	
        	ReadDataManager dm = EndpointImpl.api().getDataManager();;
        	QueryBuilder<TupleQuery> queryBuilder = QueryBuilder.createTupleQuery(lectureQuery).resolveValue(pageURI).infer(false);

        	TupleQuery query = queryBuilder.build(dm);
        	TupleQueryResult res = query.evaluate();
        	int index=0;
        	while (res.hasNext()) {
        		index++;
        		BindingSet bs = res.next();
    			ValueFactory vf = ValueFactoryImpl.getInstance();
        		URI lectureURI = vf.createURI(bs.getValue(res.getBindingNames().get(0)).stringValue());
        		if(res.hasNext())
        			createWebPage(wikiBootstrapFolder, "page"+index+".html", lectureTemplateName, lectureURI , parent, pc, false,"page"+(index+1)+".html");
        		else
        			createWebPage(wikiBootstrapFolder, "page"+index+".html", lectureTemplateName, lectureURI , parent, pc, false, "final.html");
        			
        		//logger.warn(bs.getValue(res.getBindingNames().get(0)));
        	}
        	createWebPage(wikiBootstrapFolder, "final.html", finalTemplateName, pageURI , parent, pc, true, null);

	        File zipFile = new File(storagePath, "SCORMCourse" + System.currentTimeMillis() + ".zip");
	        ZipUtil.doZipOutput(zipFile, tempDir, tempDir.listFiles());	        
	        
	        return zipFile.getName();
		} finally {
	        GenUtil.deleteRec(tempDir);
        }
    }
    
    private static void createWebPage(File folder, String pageName, String pageTemplate, 
    		URI subject, FContainer parent, PageContext pc, boolean lastPage, String linkedPage) throws IOException{
        WikiStorage ws = Wikimedia.getWikiStorage();
		ValueFactory vf = ValueFactoryImpl.getInstance();
		
        String templateContent = ws.getRawWikiContent(FluidWikiModel.resolveTemplateURI(pageTemplate,""), null);
    	String renderedPreview = SemWikiUtil.getRenderedViewContent(templateContent, subject, null, parent, pc);

    	File wikiFile = new File(folder, pageName);
        
    	String content = "<!DOCTYPE html PUBLIC\\\"-//W3C//DTD HTML 4.01 Transitional//EN\\\" \\\"http://www.w3.org/TR/html4/loose.dtd\\\">";
        content = "<html><head>";
        content += "<title>SCORM View for " + EndpointImpl.api().getRequestMapper().getReconvertableUri((URI)pc.value, true) + "</title>";
        content += "<meta http-equiv=\"Content-Type\" content=\"text/html; charset=utf-8\"><script type='text/javascript' src='../scormdriver/auto-scripts/AutoBookmark.js'></script>";
        if(lastPage)
        	content += "<script type='text/javascript' src='../scormdriver/auto-scripts/AutoCompleteSCO.js'></script>";
        content += "</head><body>";
        content += renderedPreview;
        if(!lastPage)
        	content += "<br><a href='"+linkedPage+"'><img style='border: 0px solid ; width: 92px; height: 39px;' src='next.png' alt=''></a><br>";
        content += "</body></html>";

        FileUtil.writeContentToFile(content, wikiFile.getAbsolutePath());	
    }
 
}
