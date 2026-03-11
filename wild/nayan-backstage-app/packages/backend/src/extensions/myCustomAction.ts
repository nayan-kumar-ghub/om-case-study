import { createTemplateAction } from '@backstage/plugin-scaffolder-node';
import { writeFile } from 'fs/promises';
import { join } from 'path';

export const myCustomAction = () => {
  return createTemplateAction({
    id: 'my:custom:action',
    description: 'Creates a new file in the temp workspace',

    schema: {
      input: {
        type: 'object',
        properties: {
          filename: {
            type: 'string',
            title: 'Filename',
            description: 'Name of the file to create in workspace',
          },
          contents: {
            type: 'string',
            title: 'Contents',
            description: 'Contents to write into the file',
          },
        },
      },
    },

    async handler(ctx) {
      // ctx.workspacePath is the temp folder Backstage provides
      const filePath = join(ctx.workspacePath, ctx.input.filename);

      ctx.logger.info(`Creating file: ${filePath}`);

      // Create the file in the temp workspace
      await writeFile(filePath, ctx.input.contents || 'Hello from my:custom:action');

      ctx.logger.info('File created successfully!');
    },
  });
};