import {
  JupyterFrontEnd, JupyterFrontEndPlugin
} from '@jupyterlab/application';


/**
 * Initialization data for the memorytrace extension.
 */
const extension: JupyterFrontEndPlugin<void> = {
  id: 'memorytrace',
  autoStart: true,
  activate: (app: JupyterFrontEnd) => {
    console.log('JupyterLab extension memorytrace is activated!');
  }
};

export default extension;
