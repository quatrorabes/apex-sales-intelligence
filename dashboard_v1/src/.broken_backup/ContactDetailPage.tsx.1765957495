// APEX Dashboard_v1 - Contact Detail Page
// Handles both integer IDs and UUIDs for maximum compatibility

import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Container,
  Title,
  Text,
  Card,
  Group,
  Badge,
  Stack,
  Loader,
  Button,
  Grid,
  Divider,
  Alert,
} from '@mantine/core';
import {
  IconUser,
  IconBuilding,
  IconMail,
  IconPhone,
  IconBrandLinkedin,
  IconArrowLeft,
  IconRefresh,
  IconAlertCircle,
} from '@tabler/icons-react';

const API_BASE_URL =
  (import.meta as any).env?.VITE_APEX_API_URL ||
  (import.meta as any).env?.VITE_API_URL ||
  'https://apex-sales-intelligence-api.onrender.com';

interface Contact {
  id: number;
  uuid?: string;
  name: string;
  email?: string;
  company?: string;
  title?: string;
  phone?: string;
  linkedin_url?: string;
  vertical?: string;
  persona_type?: string;
  persona_confidence?: number;
  match_tier?: string;
  match_score?: number;
  apex_score?: number;
  mdcp_score?: number;
  rss_score?: number;
  bant_total_score?: number;
  spice_total_score?: number;
  unified_qualification_score?: number;
  enrichment_status?: string;
  enriched_at?: string;
  enrichment_data?: string;
  created_at?: string;
  updated_at?: string;
}

export default function ContactDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [contact, setContact] = useState<Contact | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const isUUID = id?.includes('-') || false;

  const fetchContact = async () => {
    if (!id) {
      setError('No contact ID provided');
      setLoading(false);
      return;
    }

    setLoading(true);
    setError(null);

    try {
      let endpoint = isUUID
        ? `${API_BASE_URL}/api/contacts/uuid/${id}`
        : `${API_BASE_URL}/api/contacts/${id}`;

      let response = await fetch(endpoint);

      if (!response.ok && isUUID) {
        const listResponse = await fetch(`${API_BASE_URL}/api/v2/contacts?limit=500`);
        if (listResponse.ok) {
          const listData = await listResponse.json();
          const contacts = listData.contacts || listData.data || [];
          const found = contacts.find((c: Contact) => c.uuid === id);
          if (found) {
            setContact(found);
            setLoading(false);
            return;
          }
        }
        throw new Error('Contact not found');
      }

      if (!response.ok) {
        throw new Error(`Failed to fetch contact: ${response.status}`);
      }

      const data = await response.json();
      setContact(data.contact || data);
    } catch (err: any) {
      console.error('Fetch contact error:', err);
      setError(err.message || 'Failed to load contact');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchContact();
  }, [id]);

  const getTierColor = (tier?: string): string => {
    switch (tier?.toUpperCase()) {
      case 'HIGH': return 'green';
      case 'MEDIUM': return 'yellow';
      case 'LOW': return 'orange';
      default: return 'gray';
    }
  };

  const getScoreColor = (score?: number): string => {
    if (!score) return 'gray';
    if (score >= 80) return 'green';
    if (score >= 60) return 'teal';
    if (score >= 40) return 'yellow';
    return 'red';
  };

  if (loading) {
    return (
      <Container size="lg" py="xl">
        <Group justify="center" py="xl">
          <Loader size="lg" />
          <Text>Loading contact...</Text>
        </Group>
      </Container>
    );
  }

  if (error || !contact) {
    return (
      <Container size="lg" py="xl">
        <Alert icon={<IconAlertCircle size={16} />} title="Error Loading Contact" color="red" mb="md">
          {error || 'Contact not found'}
        </Alert>
        <Group>
          <Button leftSection={<IconArrowLeft size={16} />} onClick={() => navigate(-1)}>Go Back</Button>
          <Button leftSection={<IconRefresh size={16} />} variant="light" onClick={fetchContact}>Retry</Button>
        </Group>
      </Container>
    );
  }

  return (
    <Container size="lg" py="xl">
      <Group justify="space-between" mb="lg">
        <Group>
          <Button variant="subtle" leftSection={<IconArrowLeft size={16} />} onClick={() => navigate(-1)}>Back</Button>
          <Title order={2}>{contact.name}</Title>
          {contact.match_tier && <Badge color={getTierColor(contact.match_tier)} size="lg">{contact.match_tier} Priority</Badge>}
        </Group>
        <Group>
          {contact.enrichment_status && <Badge color={contact.enrichment_status === 'completed' ? 'green' : 'yellow'} variant="light">{contact.enrichment_status}</Badge>}
        </Group>
      </Group>

      <Grid gutter="md">
        <Grid.Col span={{ base: 12, md: 6 }}>
          <Card shadow="sm" padding="lg" radius="md" withBorder>
            <Title order={4} mb="md">Contact Information</Title>
            <Stack gap="sm">
              {contact.title && <Group><IconUser size={18} /><Text>{contact.title}</Text></Group>}
              {contact.company && <Group><IconBuilding size={18} /><Text>{contact.company}</Text></Group>}
              {contact.email && <Group><IconMail size={18} /><Text component="a" href={`mailto:${contact.email}`}>{contact.email}</Text></Group>}
              {contact.phone && <Group><IconPhone size={18} /><Text>{contact.phone}</Text></Group>}
              {contact.linkedin_url && <Group><IconBrandLinkedin size={18} /><Text component="a" href={contact.linkedin_url} target="_blank" rel="noopener noreferrer">LinkedIn Profile</Text></Group>}
            </Stack>
          </Card>
        </Grid.Col>

        <Grid.Col span={{ base: 12, md: 6 }}>
          <Card shadow="sm" padding="lg" radius="md" withBorder>
            <Title order={4} mb="md">APEX Scores</Title>
            <Stack gap="sm">
              <Group justify="space-between"><Text fw={500}>Unified Score</Text><Badge color={getScoreColor(contact.unified_qualification_score)} size="lg">{contact.unified_qualification_score || 0}</Badge></Group>
              <Divider />
              <Group justify="space-between"><Text size="sm">APEX Score</Text><Badge color={getScoreColor(contact.apex_score)} variant="light">{contact.apex_score || 0}</Badge></Group>
              <Group justify="space-between"><Text size="sm">MDCP Score</Text><Badge color={getScoreColor(contact.mdcp_score)} variant="light">{contact.mdcp_score || 0}</Badge></Group>
              <Group justify="space-between"><Text size="sm">RSS Score</Text><Badge color={getScoreColor(contact.rss_score)} variant="light">{contact.rss_score || 0}</Badge></Group>
              <Group justify="space-between"><Text size="sm">BANT Score</Text><Badge color={getScoreColor(contact.bant_total_score)} variant="light">{contact.bant_total_score || 0}</Badge></Group>
              <Group justify="space-between"><Text size="sm">SPICE Score</Text><Badge color={getScoreColor(contact.spice_total_score)} variant="light">{contact.spice_total_score || 0}</Badge></Group>
            </Stack>
          </Card>
        </Grid.Col>

        <Grid.Col span={{ base: 12, md: 6 }}>
          <Card shadow="sm" padding="lg" radius="md" withBorder>
            <Title order={4} mb="md">Classification</Title>
            <Stack gap="sm">
              <Group justify="space-between"><Text>Vertical</Text><Badge variant="outline">{contact.vertical || 'Unclassified'}</Badge></Group>
              <Group justify="space-between"><Text>Persona</Text><Badge color="blue" variant="light">{contact.persona_type || 'Unknown'}</Badge></Group>
              {contact.persona_confidence && <Group justify="space-between"><Text size="sm" c="dimmed">Confidence</Text><Text size="sm">{Math.round(contact.persona_confidence * 100)}%</Text></Group>}
              <Group justify="space-between"><Text>Match Score</Text><Badge color={getScoreColor(contact.match_score)} variant="light">{contact.match_score || 0}%</Badge></Group>
            </Stack>
          </Card>
        </Grid.Col>

        <Grid.Col span={{ base: 12, md: 6 }}>
          <Card shadow="sm" padding="lg" radius="md" withBorder>
            <Title order={4} mb="md">Metadata</Title>
            <Stack gap="sm">
              <Group justify="space-between"><Text size="sm" c="dimmed">ID</Text><Text size="sm">{contact.id}</Text></Group>
              {contact.uuid && <Group justify="space-between"><Text size="sm" c="dimmed">UUID</Text><Text size="sm" style={{ fontFamily: 'monospace', fontSize: '0.75rem' }}>{contact.uuid}</Text></Group>}
              {contact.created_at && <Group justify="space-between"><Text size="sm" c="dimmed">Created</Text><Text size="sm">{new Date(contact.created_at).toLocaleDateString()}</Text></Group>}
              {contact.enriched_at && <Group justify="space-between"><Text size="sm" c="dimmed">Enriched</Text><Text size="sm">{new Date(contact.enriched_at).toLocaleDateString()}</Text></Group>}
            </Stack>
          </Card>
        </Grid.Col>
      </Grid>
    </Container>
  );
}
