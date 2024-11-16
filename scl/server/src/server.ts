import {
  createConnection,
  TextDocuments,
  Diagnostic,
  DiagnosticSeverity,
  ProposedFeatures,
  InitializeParams,
  DidChangeConfigurationNotification,
  CompletionItem,
  CompletionItemKind,
  TextDocumentPositionParams,
  TextDocumentSyncKind,
  InitializeResult,
  MarkupContent,
  MarkupKind,
} from 'vscode-languageserver/node';

import { TextDocument } from 'vscode-languageserver-textdocument';

// Create a connection for the server, using Node's IPC as a transport.
// Also include all preview / proposed LSP features.
let connection = createConnection(ProposedFeatures.all);

// Create a simple text document manager.
let documents: TextDocuments<TextDocument> = new TextDocuments(TextDocument);

let hasConfigurationCapability: boolean = false;
let hasWorkspaceFolderCapability: boolean = false;
let hasDiagnosticRelatedInformationCapability: boolean = false;

connection.onInitialize((params: InitializeParams) => {
  let capabilities = params.capabilities;

  // Does the client support the `workspace/configuration` request?
  // If not, we fall back using global settings.
  hasConfigurationCapability = !!(
    capabilities.workspace && !!capabilities.workspace.configuration
  );
  hasWorkspaceFolderCapability = !!(
    capabilities.workspace && !!capabilities.workspace.workspaceFolders
  );
  hasDiagnosticRelatedInformationCapability = !!(
    capabilities.textDocument &&
    capabilities.textDocument.publishDiagnostics &&
    capabilities.textDocument.publishDiagnostics.relatedInformation
  );

  const result: InitializeResult = {
    capabilities: {
      textDocumentSync: TextDocumentSyncKind.Incremental,
      // Tell the client that this server supports code completion.
      completionProvider: {
        resolveProvider: true,
      },
    },
  };
  if (hasWorkspaceFolderCapability) {
    result.capabilities.workspace = {
      workspaceFolders: {
        supported: true,
      },
    };
  }
  return result;
});

connection.onInitialized(() => {
  if (hasConfigurationCapability) {
    // Register for all configuration changes.
    connection.client.register(
      DidChangeConfigurationNotification.type,
      undefined
    );
  }
  if (hasWorkspaceFolderCapability) {
    connection.workspace.onDidChangeWorkspaceFolders((_event) => {
      connection.console.log('Workspace folder change event received.');
    });
  }
});

// The example settings
interface ExampleSettings {
  maxNumberOfProblems: number;
}

// The global settings, used when the `workspace/configuration` request is not supported by the client.
// Please note that this is not the case when using this server with the client provided in this example
// but could happen with other clients.
const defaultSettings: ExampleSettings = { maxNumberOfProblems: 1000 };
let globalSettings: ExampleSettings = defaultSettings;

// Cache the settings of all open documents
let documentSettings: Map<string, Thenable<ExampleSettings>> = new Map();

connection.onDidChangeConfiguration((change) => {
  if (hasConfigurationCapability) {
    // Reset all cached document settings
    documentSettings.clear();
  } else {
    globalSettings = <ExampleSettings>(
      (change.settings.languageServerExample || defaultSettings)
    );
  }

  // Revalidate all open text documents
  documents.all().forEach(validateTextDocument);
});

function getDocumentSettings(resource: string): Thenable<ExampleSettings> {
  if (!hasConfigurationCapability) {
    return Promise.resolve(globalSettings);
  }
  let result = documentSettings.get(resource);
  if (!result) {
    result = connection.workspace.getConfiguration({
      scopeUri: resource,
      section: 'languageServerExample',
    });
    documentSettings.set(resource, result);
  }
  return result;
}

// Only keep settings for open documents
documents.onDidClose((e) => {
  documentSettings.delete(e.document.uri);
});

// The content of a text document has changed. This event is emitted
// when the text document first opened or when its content has changed.
documents.onDidChangeContent((change) => {
  validateTextDocument(change.document);
});

async function validateTextDocument(textDocument: TextDocument): Promise<void> {
  // In this simple example we get the settings for every validate run.
  let settings = await getDocumentSettings(textDocument.uri);

  // The validator creates diagnostics for all uppercase words length 2 and more
  let text = textDocument.getText();
  let pattern = /\b[A-Z]{2,}\b/g;
  let m: RegExpExecArray | null;

  let problems = 0;
  let diagnostics: Diagnostic[] = [];
  while ((m = pattern.exec(text))) {
    problems++;
    let diagnostic: Diagnostic = {
      severity: DiagnosticSeverity.Warning,
      range: {
        start: textDocument.positionAt(m.index),
        end: textDocument.positionAt(m.index + m[0].length),
      },
      message: `${m[0]} is all uppercase.`,
      source: 'ex',
    };
    if (hasDiagnosticRelatedInformationCapability) {
      diagnostic.relatedInformation = [
        {
          location: {
            uri: textDocument.uri,
            range: Object.assign({}, diagnostic.range),
          },
          message: 'Spelling matters',
        },
        {
          location: {
            uri: textDocument.uri,
            range: Object.assign({}, diagnostic.range),
          },
          message: 'Particularly for names',
        },
      ];
    }
    // diagnostics.push(diagnostic);
  }

  // Send the computed diagnostics to VS Code.
  connection.sendDiagnostics({ uri: textDocument.uri, diagnostics });
}

connection.onDidChangeWatchedFiles((_change) => {
  // Monitored files have change in VS Code
  connection.console.log('We received a file change event');
});

function filterLetters(text: string): string {
  return text
    .split('')
    .filter((c) => /^[\u4e00-\u9fa5a-z0-9]$/.test(c))
    .join('');
}

function safeMarkdown(text: string): string {
  return text.replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

// Keywords
const detail = 'Scratch Language';
type Keyword = {
  label: string;
  documentation: string;
  chinese?: string;
  example?: string;
};
const keywords: Array<Keyword> = [
  {
    label: 'const',
    documentation: '声明一个常量。',
    example: 'const a = 1;',
  },
  {
    label: 'var',
    documentation: '声明一个变量。',
    example: 'var a = 1;',
  },
  {
    label: 'if',
    documentation: '分支结构语句。',
    chinese: '如果 < > 那么',
    example: 'if (a > 1) { looks_say("a is greater than 1"); /* 或其他事 */ }',
  },
  {
    label: 'else',
    documentation: '分支结构语句。',
    chinese: '否则',
    example:
      'if (a > 1) {/* 做些事 */} else { looks_say("a is less than or equal to 1"); /* 或其他事 */ }',
  },
  {
    label: 'while',
    documentation: '循环结构语句。',
    chinese: '重复执行直到 << > 不成立>',
    example: 'while (a > 1) { looks_say("a is greater than 1"); /* 改变a */ }',
  },
  {
    label: 'until',
    documentation: '循环结构语句。',
    chinese: '重复执行直到 < >',
    example: 'until (a <= 1) { looks_say("a is greater than 1"); /* 改变a */ }',
  },
  {
    label: 'true',
    documentation: '布尔字面量“true”。表示真。',
  },
  {
    label: 'false',
    documentation: '布尔字面量“false”。表示假。',
  },
  {
    label: 'function',
    documentation: '函数定义。',
    example: 'function myFunction() { looks_say("Hello, world!"); }',
  },
  {
    label: 'clone',
    documentation: '克隆角色。',
    example: 'clone { /* 让克隆出的角色执行 */ }',
  },
  {
    label: 'array',
    documentation: '创建数组。',
    example: 'array a = [1, 2, 3];',
  },
  {
    label: 'delete',
    documentation: '删除数组的元素。',
    example: 'delete a[1];',
  },
  {
    label: 'for',
    documentation: '数组遍历。',
    example: 'for (i = anArray) { looks_say(i); /* 或其他事 */ }',
  },
  {
    label: 'attribute',
    documentation: '修改函数属性。',
    example: 'function attribute(norefresh) noRefreshFunction() { /* 做一些事 */ }',
  },
];
function createKeywordDocumentation(keyword: Keyword): MarkupContent {
  const example = keyword.example
    ? `#### 示例
\`\`\`scl
${keyword.example}
\`\`\``
    : `*当前无示例。*`;
  const chinese = keyword.chinese
    ? `#### 中文
积木中文翻译：${keyword.chinese}。`
    : `*积木无对应的中文翻译。*`;

  return {
    kind: MarkupKind.Markdown,
    value: safeMarkdown(`### 关键字：\`${keyword.label}\`
${keyword.documentation}
${example}
${chinese}`),
  };
}

// Builtin Functions
type BuiltinFunctionExtension =
  | 'music'
  | 'pen'
  | 'videoSensing'
  | 'text2speech'
  | 'translate';
type BuiltinFunction = {
  label: string;
  chinese: string;
  args: Array<string>;
  extensions?: Array<BuiltinFunctionExtension>;
};
const builtinFunctions: Array<BuiltinFunction> = [
  {
    label: 'control_delete_this_clone',
    chinese: '删除此克隆体',
    args: [],
    extensions: [],
  },
  {
    label: 'control_wait',
    chinese: '等待 (DURATION) 秒',
    args: ['DURATION'],
    extensions: [],
  },
  {
    label: 'data_addtolist',
    chinese: '将 (ITEM) 添加至 [LIST]',
    args: ['LIST', 'ITEM'],
    extensions: [],
  },
  {
    label: 'data_changevariableby',
    chinese: '将 [VARIABLE] 增加 (VALUE)',
    args: ['VARIABLE', 'VALUE'],
    extensions: [],
  },
  {
    label: 'data_deletealloflist',
    chinese: '删除 [LIST] 的全部项目',
    args: ['LIST'],
    extensions: [],
  },
  {
    label: 'data_deleteoflist',
    chinese: '删除 [LIST] 的第 (INDEX) 项',
    args: ['LIST', 'INDEX'],
    extensions: [],
  },
  {
    label: 'data_itemoflist',
    chinese: '[LIST] 的第 (INDEX) 项',
    args: ['LIST', 'INDEX'],
    extensions: [],
  },
  {
    label: 'data_lengthoflist',
    chinese: '[LIST] 的项目数',
    args: ['LIST'],
    extensions: [],
  },
  {
    label: 'data_replaceitemoflist',
    chinese: '将 [LIST] 的第 (INDEX) 项替换为 (ITEM)',
    args: ['LIST', 'INDEX', 'ITEM'],
    extensions: [],
  },
  {
    label: 'data_setvariableto',
    chinese: '将 [VARIABLE] 设为 (VALUE)',
    args: ['VARIABLE', 'VALUE'],
    extensions: [],
  },
  {
    label: 'looks_say',
    chinese: '说 (MESSAGE)',
    args: ['MESSAGE'],
    extensions: [],
  },
  {
    label: 'looks_sayforsecs',
    chinese: '说 (MESSAGE) (SECS) 秒',
    args: ['MESSAGE', 'SECS'],
    extensions: [],
  },
  {
    label: 'looks_think',
    chinese: '思考 (MESSAGE)',
    args: ['MESSAGE'],
    extensions: [],
  },
  {
    label: 'looks_thinkforsecs',
    chinese: '思考 (MESSAGE) (SECS) 秒',
    args: ['MESSAGE', 'SECS'],
    extensions: [],
  },
  {
    label: 'motion_changexby',
    chinese: '将 x 坐标增加 (DX)',
    args: ['DX'],
    extensions: [],
  },
  {
    label: 'motion_changeyby',
    chinese: '将 y 坐标增加 (DY)',
    args: ['DY'],
    extensions: [],
  },
  {
    label: 'motion_direction',
    chinese: '方向',
    args: [],
    extensions: [],
  },
  {
    label: 'motion_glidesecstoxy',
    chinese: '在 (SECS) 秒内滑行到 x: (X) y: (Y)',
    args: ['SECS', 'X', 'Y'],
    extensions: [],
  },
  {
    label: 'motion_gotoxy',
    chinese: '移到 x: (X) y: (Y)',
    args: ['X', 'Y'],
    extensions: [],
  },
  {
    label: 'motion_ifonedgebounce',
    chinese: '碰到边缘就反弹',
    args: [],
    extensions: [],
  },
  {
    label: 'motion_movesteps',
    chinese: '移动 (STEPS) 步',
    args: ['STEPS'],
    extensions: [],
  },
  {
    label: 'motion_pointindirection',
    chinese: '面向 (DIRECTION) 方向',
    args: ['DIRECTION'],
    extensions: [],
  },
  {
    label: 'motion_setx',
    chinese: '将 x 坐标设为 (X)',
    args: ['X'],
    extensions: [],
  },
  {
    label: 'motion_sety',
    chinese: '将 y 坐标设为 (Y)',
    args: ['Y'],
    extensions: [],
  },
  {
    label: 'motion_turnleft',
    chinese: '左转 (DEGREES) 度',
    args: ['DEGREES'],
    extensions: [],
  },
  {
    label: 'motion_turnright',
    chinese: '右转 (DEGREES) 度',
    args: ['DEGREES'],
    extensions: [],
  },
  {
    label: 'motion_xposition',
    chinese: 'x 坐标',
    args: [],
    extensions: [],
  },
  {
    label: 'motion_yposition',
    chinese: 'y 坐标',
    args: [],
    extensions: [],
  },
  {
    label: 'operator_add',
    chinese: '(NUM1) + (NUM2)',
    args: ['NUM1', 'NUM2'],
    extensions: [],
  },
  {
    label: 'operator_and',
    chinese: '<OPERAND1> 与 <OPERAND2>',
    args: ['OPERAND1', 'OPERAND2'],
    extensions: [],
  },
  {
    label: 'operator_contains',
    chinese: '(STRING1) 包含 (STRING2)？',
    args: ['STRING1', 'STRING2'],
    extensions: [],
  },
  {
    label: 'operator_divide',
    chinese: '(NUM1) / (NUM2)',
    args: ['NUM1', 'NUM2'],
    extensions: [],
  },
  {
    label: 'operator_equals',
    chinese: '(OPERAND1) = (OPERAND2)',
    args: ['OPERAND1', 'OPERAND2'],
    extensions: [],
  },
  {
    label: 'operator_gt',
    chinese: '(OPERAND1) > (OPERAND2)',
    args: ['OPERAND1', 'OPERAND2'],
    extensions: [],
  },
  {
    label: 'operator_join',
    chinese: '连接 (STRING1) 和 (STRING2)',
    args: ['STRING1', 'STRING2'],
    extensions: [],
  },
  {
    label: 'operator_letter_of',
    chinese: '(STRING) 的第 (LETTER) 个字符',
    args: ['STRING', 'LETTER'],
    extensions: [],
  },
  {
    label: 'operator_lt',
    chinese: '(OPERAND1) < (OPERAND2)',
    args: ['OPERAND1', 'OPERAND2'],
    extensions: [],
  },
  {
    label: 'operator_mod',
    chinese: '(NUM1) 除以 (NUM2) 的余数',
    args: ['NUM1', 'NUM2'],
    extensions: [],
  },
  {
    label: 'operator_multiply',
    chinese: '(NUM1) * (NUM2)',
    args: ['NUM1', 'NUM2'],
    extensions: [],
  },
  {
    label: 'operator_not',
    chinese: '<OPERAND> 不成立',
    args: ['OPERAND'],
    extensions: [],
  },
  {
    label: 'operator_or',
    chinese: '<OPERAND1> 或 <OPERAND2>',
    args: ['OPERAND1', 'OPERAND2'],
    extensions: [],
  },
  {
    label: 'operator_subtract',
    chinese: '(NUM1) - (NUM2)',
    args: ['NUM1', 'NUM2'],
    extensions: [],
  },
  {
    label: 'pen_changePenSizeBy',
    chinese: '将笔的粗细增加 (SIZE)',
    args: ['SIZE'],
    extensions: ['pen'],
  },
  {
    label: 'pen_clear',
    chinese: '全部擦除',
    args: [],
    extensions: ['pen'],
  },
  {
    label: 'pen_penDown',
    chinese: '落笔',
    args: [],
    extensions: ['pen'],
  },
  {
    label: 'pen_penUp',
    chinese: '抬笔',
    args: [],
    extensions: ['pen'],
  },
  {
    label: 'pen_setPenColorToColor',
    chinese: '将笔的颜色设为 (COLOR)',
    args: ['COLOR'],
    extensions: ['pen'],
  },
  {
    label: 'pen_setPenSizeTo',
    chinese: '将笔的粗细设为 (SIZE)',
    args: ['SIZE'],
    extensions: ['pen'],
  },
  {
    label: 'pen_stamp',
    chinese: '图章',
    args: [],
    extensions: ['pen'],
  },
  {
    label: 'sensing_answer',
    chinese: '回答',
    args: [],
    extensions: [],
  },
  {
    label: 'sensing_askandwait',
    chinese: '询问 (QUESTION) 并等待',
    args: ['QUESTION'],
    extensions: [],
  },
  {
    label: 'sensing_loudness',
    chinese: '响度',
    args: [],
    extensions: [],
  },
];
function createBuiltinFunctionDocumentation(
  builtinFunction: BuiltinFunction
): MarkupContent {
  const chinese = builtinFunction.chinese
    ? `#### 中文
积木中文翻译：${builtinFunction.chinese}。`
    : `*积木无对应的中文翻译。*`;
  const args =
    builtinFunction.args.length > 0
      ? `#### 参数
调用参数列表顺序：${builtinFunction.args
          .map((arg) => `\`${arg}\``)
          .join('，')}。`
      : `*调用不需要传递参数。*`;
  const extensions =
    builtinFunction.extensions.length > 0
      ? `#### 扩展
积木属于扩展：${builtinFunction.extensions
          .map((ext) => `\`${ext}\``)
          .join('，')}。`
      : `*积木不属于任何扩展。*`;

  return {
    kind: MarkupKind.Markdown,
    value: safeMarkdown(`### 内置函数：\`${builtinFunction.label}\`
${chinese}
${args}
${extensions}`),
  };
}

// This handler provides the initial list of the completion items.
connection.onCompletion(
  (textDocumentPosition: TextDocumentPositionParams): CompletionItem[] => {
    // The pass parameter contains the position of the text document in
    // which code complete got requested. For the example we ignore this
    // info and always provide the same completion items.
    let text = documents.get(textDocumentPosition.textDocument.uri).getText();
    return [
      ...keywords.map((keyword) => ({
        label: keyword.label,
        kind: CompletionItemKind.Keyword,
        data: { keyword },
      })),
      ...builtinFunctions.map((builtinFunction) => ({
        label: builtinFunction.label,
        kind: CompletionItemKind.Function,
        data: { builtinFunction },
      })),
      ...builtinFunctions.map((builtinFunction) => ({
        label: filterLetters(builtinFunction.chinese),
        insertText: builtinFunction.label,
        kind: CompletionItemKind.Function,
        data: { builtinFunction },
      })),
    ];
  }
);

// This handler resolves additional information for the item selected in
// the completion list.
connection.onCompletionResolve((item: CompletionItem): CompletionItem => {
  const { keyword, builtinFunction } = item.data;
  item.detail = detail;
  if (keyword) {
    item.documentation = createKeywordDocumentation(keyword);
  }
  if (builtinFunction) {
    item.documentation = createBuiltinFunctionDocumentation(builtinFunction);
  }
  return item;
});

// Make the text document manager listen on the connection
// for open, change and close text document events
documents.listen(connection);

// Listen on the connection
connection.listen();
