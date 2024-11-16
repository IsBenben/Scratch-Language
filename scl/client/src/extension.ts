import * as path from 'path';
import {
  workspace as Workspace,
  window as Window,
  ExtensionContext,
  TextDocument,
  OutputChannel,
  WorkspaceFolder,
  Uri,
  commands,
  Terminal,
} from 'vscode';

import {
  LanguageClient,
  LanguageClientOptions,
  TransportKind,
} from 'vscode-languageclient/node';

let defaultClient: LanguageClient;
const clients = new Map<string, LanguageClient>();

let _sortedWorkspaceFolders: string[] | undefined;
function sortedWorkspaceFolders(): string[] {
  if (_sortedWorkspaceFolders === void 0) {
    _sortedWorkspaceFolders = Workspace.workspaceFolders
      ? Workspace.workspaceFolders
          .map((folder) => {
            let result = folder.uri.toString();
            if (result.charAt(result.length - 1) !== '/') {
              result = result + '/';
            }
            return result;
          })
          .sort((a, b) => {
            return a.length - b.length;
          })
      : [];
  }
  return _sortedWorkspaceFolders;
}
Workspace.onDidChangeWorkspaceFolders(
  () => (_sortedWorkspaceFolders = undefined)
);

function getOuterMostWorkspaceFolder(folder: WorkspaceFolder): WorkspaceFolder {
  const sorted = sortedWorkspaceFolders();
  for (const element of sorted) {
    let uri = folder.uri.toString();
    if (uri.charAt(uri.length - 1) !== '/') {
      uri = uri + '/';
    }
    if (uri.startsWith(element)) {
      return Workspace.getWorkspaceFolder(Uri.parse(element))!;
    }
  }
  return folder;
}

let terminal: Terminal | null = null;

export function activate(context: ExtensionContext) {
  const module = context.asAbsolutePath(
    path.join('server', 'out', 'server.js')
  );
  const outputChannel: OutputChannel =
    Window.createOutputChannel('Scratch-Language');

  function didOpenTextDocument(document: TextDocument): void {
    // We are only interested in language mode text
    if (
      document.languageId !== 'scl' ||
      (document.uri.scheme !== 'file' && document.uri.scheme !== 'untitled')
    ) {
      return;
    }

    const uri = document.uri;
    // Untitled files go to a default client.
    if (uri.scheme === 'untitled' && !defaultClient) {
      const serverOptions = {
        run: { module, transport: TransportKind.ipc },
        debug: { module, transport: TransportKind.ipc },
      };
      const clientOptions: LanguageClientOptions = {
        documentSelector: [{ scheme: 'untitled', language: 'scl' }],
        diagnosticCollectionName: 'Scratch-Language',
        outputChannel: outputChannel,
      };
      defaultClient = new LanguageClient(
        'Scratch-Language',
        'Scratch Language',
        serverOptions,
        clientOptions
      );
      defaultClient.start();
      return;
    }
    let folder = Workspace.getWorkspaceFolder(uri);
    // Files outside a folder can't be handled. This might depend on the language.
    // Single file languages like JSON might handle files outside the workspace folders.
    if (!folder) {
      return;
    }
    // If we have nested workspace folders we only start a server on the outer most workspace folder.
    folder = getOuterMostWorkspaceFolder(folder);

    if (!clients.has(folder.uri.toString())) {
      const serverOptions = {
        run: { module, transport: TransportKind.ipc },
        debug: { module, transport: TransportKind.ipc },
      };
      const clientOptions: LanguageClientOptions = {
        documentSelector: [
          {
            scheme: 'file',
            language: 'scl',
            pattern: `${folder.uri.fsPath}/**/*`,
          },
        ],
        diagnosticCollectionName: 'Scratch-Language',
        workspaceFolder: folder,
        outputChannel: outputChannel,
      };
      const client = new LanguageClient(
        'Scratch-Language',
        'Scratch Language',
        serverOptions,
        clientOptions
      );
      client.start();
      clients.set(folder.uri.toString(), client);
    }
  }

  Workspace.onDidOpenTextDocument(didOpenTextDocument);
  Workspace.textDocuments.forEach(didOpenTextDocument);
  Workspace.onDidChangeWorkspaceFolders((event) => {
    for (const folder of event.removed) {
      const client = clients.get(folder.uri.toString());
      if (client) {
        clients.delete(folder.uri.toString());
        client.stop();
      }
    }
  });
  Workspace.onDidChangeConfiguration((event) => {
    
  })

  const run = commands.registerCommand(
    'scl.runCode',
    (fileUri: Uri) => {
      let isNewTerminal = false;
      if (terminal === null) {
          terminal = Window.createTerminal("Code");
          isNewTerminal = true;
      }
      terminal.show();
      terminal.sendText(`scl run ${fileUri.fsPath}`);
    }
  );

  context.subscriptions.push(run);
}

export function deactivate(): Thenable<void> {
  const promises: Thenable<void>[] = [];
  if (defaultClient) {
    promises.push(defaultClient.stop());
  }
  for (const client of clients.values()) {
    promises.push(client.stop());
  }
  return Promise.all(promises).then(() => undefined);
}