import { createBackendModule } from '@backstage/backend-plugin-api';
import { scaffolderActionsExtensionPoint } from '@backstage/plugin-scaffolder-node/alpha';
import { myCustomAction } from './myCustomAction';

// Registers our custom action with the Backstage scaffolder
export const scaffolderModuleCustomAction = createBackendModule({
  pluginId: 'scaffolder',
  moduleId: 'custom-action',

  register(reg) {
    reg.registerInit({
      deps: {
        scaffolder: scaffolderActionsExtensionPoint,
      },
      async init({ scaffolder }) {
        scaffolder.addActions(myCustomAction());
      },
    });
  },
});