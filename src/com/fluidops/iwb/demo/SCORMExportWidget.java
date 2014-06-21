package com.fluidops.iwb.demo;

import java.io.IOException;

import org.apache.log4j.Logger;
import org.openrdf.model.ValueFactory;
import org.openrdf.model.impl.ValueFactoryImpl;

import sun.rmi.runtime.Log;

import com.fluidops.ajax.FClientUpdate;
import com.fluidops.ajax.components.FButton;
import com.fluidops.ajax.components.FComponent;
import com.fluidops.ajax.components.FContainer;
import com.fluidops.ajax.components.FLabel;
import com.fluidops.ajax.components.FPopupWindow;
import com.fluidops.ajax.components.FTextInput2;
import com.fluidops.iwb.api.EndpointImpl;
import com.fluidops.iwb.api.ReadDataManager;
import com.fluidops.iwb.api.WikiStorageBulkServiceImpl;
import com.fluidops.iwb.model.ParameterConfigDoc;
import com.fluidops.iwb.server.AbstractFileServlet;
import com.fluidops.iwb.widget.AbstractWidget;
import com.fluidops.util.Rand;
import com.sun.org.apache.xerces.internal.util.URI;


/**
 * On some wiki page add
 * 
 * <code>
 * = Test my demo widget =
 * 
 * <br/>
 * {{#widget: com.fluidops.iwb.widget.MyDemoWidget 
 * | labelText = 'Enter your name'
 * }}
 * 
 * </code>
 * 
 */
public class SCORMExportWidget extends AbstractWidget<SCORMExportWidget.Config> {
	private static final Logger logger = Logger.getLogger(EndpointImpl.class.getName());

	public static class Config{
		
		@ParameterConfigDoc(desc = "Title Page Template", required = true)
		public String titlePageTemplate;
		@ParameterConfigDoc(desc = "Lecture Page Template", required = true)
		public String lecturePageTemplate;
		@ParameterConfigDoc(desc = "Lecture Query", required = true)
		public String lectureQuery;
		@ParameterConfigDoc(desc = "Final Page Template", required = true)
		public String finalPageTemplate;

	}

	@Override
	protected FComponent getComponent(String id) {
		final Config config = get();
		FContainer cnt = new FContainer(id);
		FButton btnOk = new FButton("btn_generate_SCORM", "Generate SCORM") {
			@Override
			public void onClick() {
				generateSCORM(this);				
			}
		};
		btnOk.addStyle("margin-left", "10px");
		cnt.add(btnOk);
		
		return cnt;
	}	

	public String getTitle() {
		return "My first widget";
	}

	public Class<?> getConfigClass() {
		return Config.class;
	}

	protected void generateSCORM(FComponent comp){
			
		try {
			ValueFactory vf = ValueFactoryImpl.getInstance();
			FContainer cnt = new FContainer("212");
			final Config config = get();
			String fileName = SCORMExportService.createWikiBootstrap(vf.createURI(pc.value.stringValue()),
					config.titlePageTemplate, config.finalPageTemplate, config.lecturePageTemplate, config.lectureQuery,
					cnt,pc);
			final FPopupWindow p = comp.getPage().getPopupWindowInstance("Export created successfully: " + fileName);
			p.add(createExportDownloadButton(fileName), "floatLeft");
			p.addCloseButton("Close");
			p.populateAndShow();
		} catch (Exception e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}
	
	protected static FButton createExportDownloadButton(final String fileName) {
		return new FButton("b"+Rand.getIncrementalFluidUUID(), "Download") {			
			@Override
			public void onClick() {
				String downloadFileName = SCORMExportService.WIKIEXPORT_STORAGE.replace("\\", "/") + fileName;	    
				//String downloadFileName = "mocky_mock";
				addClientUpdate(new FClientUpdate("document.location='"+
						EndpointImpl.api().getRequestMapper().getContextPath()+
						"/file/?file="+downloadFileName+"&type=zip&root="+
						AbstractFileServlet.RootDirectory.IWB_WORKING_DIR+"'"));
		        //EndpointImpl.api().getPrinter().print(pc, resp);
			}
		};
	}
}